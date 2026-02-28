"""
独立弹窗脚本 - 由 btc_monitor.py 通过 subprocess 调用
用法: pythonw popup.py "标题" "消息内容"
"""
import sys
import tkinter as tk

def show_popup(title: str, message: str, duration_ms: int = 8000) -> None:
    root = tk.Tk()
    root.overrideredirect(True)
    root.wm_attributes('-topmost', True)
    root.configure(bg='#1e1e2e')

    frame = tk.Frame(root, bg='#1e1e2e', padx=16, pady=12)
    frame.pack()

    header = tk.Frame(frame, bg='#1e1e2e')
    header.pack(fill='x')

    indicator = tk.Label(header, text='●', fg='#f38ba8', bg='#1e1e2e', font=('Segoe UI', 10))
    indicator.pack(side='left')

    title_label = tk.Label(
        header, text=title, fg='#cdd6f4', bg='#1e1e2e',
        font=('Segoe UI', 11, 'bold'), padx=6
    )
    title_label.pack(side='left')

    msg_label = tk.Label(
        frame, text=message, fg='#a6adc8', bg='#1e1e2e',
        font=('Segoe UI', 10), justify='left', wraplength=280
    )
    msg_label.pack(anchor='w', pady=(6, 0))

    # 定位到右下角
    root.update_idletasks()
    win_w = root.winfo_reqwidth()
    win_h = root.winfo_reqheight()
    scr_w = root.winfo_screenwidth()
    scr_h = root.winfo_screenheight()
    x = scr_w - win_w - 20
    y = scr_h - win_h - 60
    root.geometry(f'{win_w}x{win_h}+{x}+{y}')

    root.after(duration_ms, root.destroy)
    root.mainloop()

if __name__ == '__main__':
    title = sys.argv[1] if len(sys.argv) > 1 else 'BTC Alert'
    message = sys.argv[2] if len(sys.argv) > 2 else 'Price target reached!'
    show_popup(title, message)
