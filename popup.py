"""
独立弹窗脚本 - 滴答清单风格 UI
由 btc_monitor.py 通过 subprocess 调用
用法: pythonw popup.py "标题" "消息内容"
"""
import sys
import subprocess
import tkinter as tk
from tkinter import font as tkfont
import time
from datetime import datetime

# ──────────────────────────────────────────────
# Snooze 配置：可在此处自由添加更多选项
SNOOZE_OPTIONS = [
    ("15 分钟", 15 * 60),
    ("30 分钟", 30 * 60),
]


class SnoozePicker:
    """
    稍后提醒时间选择浮窗（Toplevel，不新建 Tk）。
    弹出于"稍后提醒"按钮正上方。
    """
    def __init__(self, parent, anchor_x, anchor_y, options):
        self.result_seconds = None
        self._build(parent, anchor_x, anchor_y, options)

    def _build(self, parent, ax, ay, options):
        item_h = 40
        w = 150
        h = item_h * len(options) + 16

        menu_x = ax
        menu_y = ay - h - 6

        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", True)
        self.win.geometry(f"{w}x{h}+{menu_x}+{menu_y}")
        self.win.configure(bg="#ffffff")

        # 白色背景 + 边框
        outer = tk.Frame(self.win, bg="#e0e0e0", padx=1, pady=1)
        outer.pack(fill="both", expand=True)
        inner = tk.Frame(outer, bg="#ffffff")
        inner.pack(fill="both", expand=True, padx=0, pady=0)

        for label, seconds in options:
            row = tk.Frame(inner, bg="#ffffff", cursor="hand2")
            row.pack(fill="x", pady=2, padx=8)
            lbl = tk.Label(row, text=label, bg="#ffffff", fg="#222222",
                           font=("Segoe UI", 10), anchor="w", pady=8, padx=10)
            lbl.pack(fill="x")
            # 悬停效果
            for widget in (row, lbl):
                widget.bind("<Enter>", lambda e, r=row, l=lbl: (r.config(bg="#f0f4ff"), l.config(bg="#f0f4ff")))
                widget.bind("<Leave>", lambda e, r=row, l=lbl: (r.config(bg="#ffffff"), l.config(bg="#ffffff")))
                widget.bind("<Button-1>", lambda e, s=seconds: self._select(s))

        # 点击窗口外部关闭
        self.win.bind("<FocusOut>", lambda e: self._cancel())
        self.win.focus_force()

    def _select(self, seconds):
        self.result_seconds = seconds
        self.win.destroy()

    def _cancel(self):
        self.win.destroy()


class TickTickPopup:
    """
    主弹窗 —— 滴答清单风格，无 -transparentcolor，兼容性更好。
    用带颜色的外边框 Frame 模拟圆角阴影感。
    """
    WIDTH  = 340
    HEIGHT = 165

    def __init__(self, title, message):
        self.title_text   = title
        self.message_text = message
        self.action       = None

    def show(self):
        W, H = self.WIDTH, self.HEIGHT
        root = self.root = tk.Tk()
        root.overrideredirect(True)
        root.wm_attributes("-topmost", True)
        root.configure(bg="#d0d0d0")   # 阴影色边框

        # 定位到右下角
        root.update_idletasks()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        rx = sw - W - 20
        ry = sh - H - 60
        root.geometry(f"{W}x{H}+{rx}+{ry}")

        # 外层阴影边框 (1px 灰色)
        border = tk.Frame(root, bg="#e0e0e0", padx=1, pady=1)
        border.pack(fill="both", expand=True)

        # 白色主卡片
        card = tk.Frame(border, bg="#ffffff")
        card.pack(fill="both", expand=True)

        # ──── Header ────────────────────────────
        hdr = tk.Frame(card, bg="#ffffff", padx=16, pady=12)
        hdr.pack(fill="x")

        tk.Label(hdr, text="◉", font=("Segoe UI", 13),
                 fg="#f7a030", bg="#ffffff").pack(side="left", padx=(0, 6))
        tk.Label(hdr, text=datetime.now().strftime("今天 %H:%M"),
                 font=("Segoe UI", 11), fg="#4a6cf7", bg="#ffffff").pack(side="left")

        x_btn = tk.Label(hdr, text="✕", font=("Segoe UI", 11),
                         fg="#aaaaaa", bg="#ffffff", cursor="hand2")
        x_btn.pack(side="right")
        x_btn.bind("<Button-1>", lambda e: self._on_close())
        x_btn.bind("<Enter>", lambda e: x_btn.config(fg="#555555"))
        x_btn.bind("<Leave>", lambda e: x_btn.config(fg="#aaaaaa"))

        # ──── 消息正文 ──────────────────────────
        tk.Label(card, text=self.message_text,
                 fg="#222222", bg="#ffffff",
                 font=("Segoe UI", 11), justify="left",
                 wraplength=W - 32, anchor="nw",
                 padx=16, pady=0).pack(fill="x")

        # ──── 底部按钮 ──────────────────────────
        btn_frame = tk.Frame(card, bg="#ffffff", padx=12, pady=12)
        btn_frame.pack(fill="x", side="bottom")

        # 完成按钮
        done_btn = tk.Button(
            btn_frame, text="完成", bg="#4a6cf7", fg="#ffffff",
            font=("Segoe UI", 10), relief="flat", cursor="hand2",
            padx=0, pady=6, activebackground="#3a5ce5", activeforeground="#ffffff",
            command=self._on_done
        )
        done_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        # 稍后提醒按钮
        self._snooze_btn = tk.Button(
            btn_frame, text="稍后提醒", bg="#ffffff", fg="#555555",
            font=("Segoe UI", 10), relief="flat", cursor="hand2",
            padx=0, pady=6, bd=1, highlightbackground="#cccccc",
            activebackground="#f5f5f5", activeforeground="#333333",
        )
        self._snooze_btn.config(
            command=lambda: self._on_snooze_click(rx, ry, H)
        )
        self._snooze_btn.pack(side="left", fill="x", expand=True)

        # 给稍后提醒按钮加描边
        snooze_wrap = tk.Frame(btn_frame, bg="#cccccc", padx=1, pady=1)
        # 注意：需要重新pack，用 Frame 包裹按钮实现边框
        self._snooze_btn.pack_forget()
        snooze_wrap.pack(side="left", fill="x", expand=True)
        self._snooze_btn = tk.Button(
            snooze_wrap, text="稍后提醒", bg="#ffffff", fg="#555555",
            font=("Segoe UI", 10), relief="flat", cursor="hand2",
            padx=0, pady=6, activebackground="#f5f5f5", activeforeground="#333333",
        )
        self._snooze_btn.config(command=lambda: self._on_snooze_click(rx, ry, H))
        self._snooze_btn.pack(fill="both")

        root.mainloop()
        return self.action

    def _on_done(self):
        self.action = "done"
        self.root.destroy()

    def _on_close(self):
        self.action = "close"
        self.root.destroy()

    def _on_snooze_click(self, win_x, win_y, win_h):
        """在稍后提醒按钮上方弹出时间选择菜单"""
        # 稍后提醒按钮大约在窗口右下角，计算绝对坐标
        anchor_x = win_x + self.WIDTH // 2
        anchor_y = win_y + win_h - 25

        picker = SnoozePicker(self.root, anchor_x, anchor_y, SNOOZE_OPTIONS)
        self.root.wait_window(picker.win)

        if picker.result_seconds is not None:
            self.action = ("snooze", picker.result_seconds)
            self.root.destroy()
        # 如果取消（点击菜单外），主弹窗继续


def start_alert_loop(title, message):
    """
    显示弹窗，处理用户动作。
    稍后提醒：休眠结束后重新以子进程启动自身。
    （tkinter 同一进程不支持多个 Tk() 根窗口，故用子进程方案）
    """
    popup = TickTickPopup(title, message)
    action = popup.show()

    if isinstance(action, tuple) and action[0] == "snooze":
        seconds = action[1]
        time.sleep(seconds)
        # 用 pythonw.exe 重新启动自身（无控制台黑窗口）
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        subprocess.Popen([pythonw, __file__, title, message])
    # "done" 或 "close" 时退出


if __name__ == "__main__":
    title   = sys.argv[1] if len(sys.argv) > 1 else "BTC Alert"
    message = sys.argv[2] if len(sys.argv) > 2 else "BTC 价格已达到目标！"
    start_alert_loop(title, message)
