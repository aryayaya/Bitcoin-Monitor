import sys
import json
import tkinter as tk
from tkinter import messagebox

class ConfigPopup:
    WIDTH = 340
    HEIGHT = 240

    def __init__(self, price=65900.0, interval=5, direction="greater"):
        self.price = price
        self.interval = interval
        self.direction = direction
        self.result = None

    def show(self):
        W, H = self.WIDTH, self.HEIGHT
        root = self.root = tk.Tk()
        root.overrideredirect(True)
        root.wm_attributes("-topmost", True)
        root.configure(bg="#d0d0d0")
        
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw - W) // 2
        y = (sh - H) // 2
        root.geometry(f"{W}x{H}+{x}+{y}")

        border = tk.Frame(root, bg="#e0e0e0", padx=1, pady=1)
        border.pack(fill="both", expand=True)

        card = tk.Frame(border, bg="#ffffff")
        card.pack(fill="both", expand=True)

        hdr = tk.Frame(card, bg="#ffffff", padx=16, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="◉", font=("Segoe UI", 13), fg="#f7a030", bg="#ffffff").pack(side="left", padx=(0, 6))
        tk.Label(hdr, text="参数设置", font=("Segoe UI", 11, "bold"), fg="#4a6cf7", bg="#ffffff").pack(side="left")

        x_btn = tk.Label(hdr, text="✕", font=("Segoe UI", 11), fg="#aaaaaa", bg="#ffffff", cursor="hand2")
        x_btn.pack(side="right")
        x_btn.bind("<Button-1>", lambda e: self._on_close())
        x_btn.bind("<Enter>", lambda e: x_btn.config(fg="#555555"))
        x_btn.bind("<Leave>", lambda e: x_btn.config(fg="#aaaaaa"))

        body = tk.Frame(card, bg="#ffffff", padx=20, pady=0)
        body.pack(fill="both", expand=True)

        # Target Price
        row1 = tk.Frame(body, bg="#ffffff")
        row1.pack(fill="x", pady=8)
        tk.Label(row1, text="目标价格 (USDT)", font=("Segoe UI", 10), bg="#ffffff", fg="#333333").pack(side="left")
        self.price_var = tk.StringVar(value=str(self.price))
        entry_price = tk.Entry(row1, textvariable=self.price_var, font=("Segoe UI", 10), width=12, justify="center", bd=1, bg="#fafafa", relief="solid")
        entry_price.pack(side="right")
        entry_price.focus_set()
        entry_price.select_range(0, tk.END)

        # Direction
        row2 = tk.Frame(body, bg="#ffffff")
        row2.pack(fill="x", pady=8)
        tk.Label(row2, text="触发条件", font=("Segoe UI", 10), bg="#ffffff", fg="#333333").pack(side="left")
        
        dir_frame = tk.Frame(row2, bg="#ffffff")
        dir_frame.pack(side="right")
        self.dir_var = tk.StringVar(value=self.direction)
        
        tk.Radiobutton(dir_frame, text="≥ 大于", variable=self.dir_var, value="greater", bg="#ffffff", fg="#333333", font=("Segoe UI", 9), activebackground="#ffffff").pack(side="left", padx=2)
        tk.Radiobutton(dir_frame, text="≤ 小于", variable=self.dir_var, value="less", bg="#ffffff", fg="#333333", font=("Segoe UI", 9), activebackground="#ffffff").pack(side="left", padx=2)

        # Interval
        row3 = tk.Frame(body, bg="#ffffff")
        row3.pack(fill="x", pady=8)
        tk.Label(row3, text="轮询间隔 (分钟)", font=("Segoe UI", 10), bg="#ffffff", fg="#333333").pack(side="left")
        self.interval_var = tk.StringVar(value=str(self.interval))
        tk.Entry(row3, textvariable=self.interval_var, font=("Segoe UI", 10), width=12, justify="center", bd=1, bg="#fafafa", relief="solid").pack(side="right")

        # Bottom Button
        btn_frame = tk.Frame(card, bg="#ffffff", padx=16, pady=16)
        btn_frame.pack(fill="x", side="bottom")

        done_btn = tk.Button(
            btn_frame, text="确认启动", bg="#4a6cf7", fg="#ffffff",
            font=("Segoe UI", 10), relief="flat", cursor="hand2",
            padx=0, pady=6, activebackground="#3a5ce5", activeforeground="#ffffff",
            command=self._on_done
        )
        done_btn.pack(side="left", fill="x", expand=True)
        
        root.bind("<Return>", lambda e: self._on_done())
        root.mainloop()
        return self.result

    def _on_done(self):
        try:
            p = float(self.price_var.get())
            i = int(self.interval_var.get())
            if p <= 0 or i <= 0:
                raise ValueError
            self.result = {
                "price": p,
                "interval": i,
                "direction": self.dir_var.get()
            }
            self.root.destroy()
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字！\n价格和间隔必须大于 0", parent=self.root)

    def _on_close(self):
        self.result = None
        self.root.destroy()

if __name__ == "__main__":
    price = float(sys.argv[1]) if len(sys.argv) > 1 else 65900.0
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    direction = sys.argv[3] if len(sys.argv) > 3 else "greater"
    
    popup = ConfigPopup(price, interval, direction)
    res = popup.show()
    # 打印 JSON 供父进程读取
    if res:
        print(json.dumps(res))
    else:
        # 如果用户关闭窗口，默认使用进入时的参数
        print(json.dumps({"price": price, "interval": interval, "direction": direction}))
