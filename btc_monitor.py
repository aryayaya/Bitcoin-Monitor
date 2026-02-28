import os
import sys
import time
import requests
import subprocess
from typing import Protocol
import schedule
import logging
import argparse

# ==========================================
# 1. 协议定义 (Protocols)
# ==========================================

class PriceFetcher(Protocol):
    def fetch_price(self) -> float:
        """获取并返回当前价格"""
        ...

class Notifier(Protocol):
    def send_notification(self, title: str, message: str) -> None:
        """发送通知"""
        ...

class AlertStrategy(Protocol):
    def should_alert(self, current_price: float) -> bool:
        """判断是否应该触发警报"""
        ...

# ==========================================
# 2. 具体实现 (Implementations)
# ==========================================

class BinancePriceFetcher:
    def fetch_price(self) -> float:
        try:
            # 使用币安的公开API获取BTCUSDT的最新价格
            url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return float(data['price'])
        except Exception as e:
            logging.error(f"Failed to fetch price from Binance: {e}")
            return 0.0

class WindowsToastNotifier:
    """
    通过 subprocess 启动独立的 popup.py GUI 进程来显示右下角弹窗。
    独立进程拥有完整的 GUI 上下文，可靠地显示 tkinter 窗口。
    使用 pythonw.exe 避免弹出额外的控制台黑窗口。
    """
    # popup.py 与本文件同目录
    POPUP_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'popup.py')

    def send_notification(self, title: str, message: str) -> None:
        try:
            # pythonw.exe = 无控制台窗口的 Python 解释器
            pythonw = sys.executable.replace('python.exe', 'pythonw.exe')
            subprocess.Popen(
                [pythonw, self.POPUP_SCRIPT, title, message],
                close_fds=True
            )
        except Exception as e:
            logging.error(f"Failed to launch popup process: {e}")


class TargetPriceStrategy:
    def __init__(self, target_price: float):
        self.target_price = target_price
        # 记录上一次是否已经报警，避免在目标价格之上时一直弹出
        self.already_alerted = False

    def should_alert(self, current_price: float) -> bool:
        if current_price >= self.target_price:
            if not self.already_alerted:
                self.already_alerted = True
                return True
        else:
            # 如果价格又回落了，重置警报状态，下次到达再提醒
            self.already_alerted = False
            
        return False

# ==========================================
# 3. 监控应用主类 (Controller)
# ==========================================

class MonitorApp:
    def __init__(self, fetcher: PriceFetcher, notifier: Notifier, strategy: AlertStrategy):
        self.fetcher = fetcher
        self.notifier = notifier
        self.strategy = strategy

    def run_check(self) -> None:
        logging.info("Checking BTC price...")
        current_price = self.fetcher.fetch_price()
        if current_price <= 0:
            logging.warning("Invalid price retrieved. Skipping this check.")
            return

        logging.info(f"Current BTC Price: ${current_price}")

        if self.strategy.should_alert(current_price):
            msg = f"BTC Price has reached your target!\nCurrent Price: ${current_price}"
            logging.info(f"Alert triggered: {msg}")
            self.notifier.send_notification("BTC Price Alert", msg)

# ==========================================
# 4. 主程序入口 (Main)
# ==========================================

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="BTC Price Monitor")
    parser.add_argument('--test-fetch', action='store_true', help='Test price fetching independently')
    parser.add_argument('--test-notify', action='store_true', help='Test notification system independently')
    args = parser.parse_args()

    # 实例化组件
    fetcher = BinancePriceFetcher()
    notifier = WindowsToastNotifier()
    strategy = TargetPriceStrategy(target_price=65900.0)

    if args.test_fetch:
        price = fetcher.fetch_price()
        print(f"Fetch Test: Current BTC Price is ${price}")
        return

    if args.test_notify:
        print("Notification Test: A popup should appear in the bottom-right corner...")
        notifier.send_notification("Test Alert", "This is a test notification from BTC Monitor.")
        time.sleep(1)  # 给 Popen 启动时间
        return

    app = MonitorApp(fetcher, notifier, strategy)

    logging.info("Starting BTC Monitor... Will check every 5 minutes.")
    # 先立即执行一次
    app.run_check()
    
    # 每5分钟执行一次
    schedule.every(5).minutes.do(app.run_check)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
