# -*- coding: gbk -*-
import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style
import threading
import pyperclip
import pyautogui
import keyboard
import time
import os

class TypingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("去你大爷的禁止粘贴  --by Doudou0611")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        self.center_window()

        # 设置窗口图标（使用 .ico 文件，确保路径正确）
        icon_path = "FuckingProhibitPasting\icon.ico"
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                print("图标加载失败:", e)

        self.style = Style("superhero")
        self.style.master = self.root

        self.typing_interval = tk.DoubleVar(value=0.05)
        self.mode_var = tk.StringVar(value="逐字打字")
        self.last_clipboard_text = ""
        self.typing_thread = None
        self.stop_typing_flag = False
        self.exit_flag = False

        self.build_ui()
        self.start_clipboard_listener()
        self.start_hotkey_listener()

        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    def quit_app(self):
        self.exit_flag = True
        self.root.quit()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")

    def build_ui(self):
        self.text_box = tk.Text(self.root, height=8, font=("Consolas", 12))
        self.text_box.pack(padx=10, pady=(15, 10), fill="both", expand=True)

        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=(0, 5))
        tk.Label(mode_frame, text="输入模式: ").pack(side="left")
        tk.OptionMenu(mode_frame, self.mode_var, "逐字打字", "快速粘贴").pack(side="left")

        speed_frame = tk.Frame(self.root)
        speed_frame.pack(pady=5)
        tk.Label(speed_frame, text="打字间隔 (0.005 ~ 1 秒): ").pack(side="left")
        self.speed_entry = tk.Entry(speed_frame, textvariable=self.typing_interval, width=6)
        self.speed_entry.pack(side="left")

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="立即输入", command=self.manual_trigger).pack(side="left", padx=5)

        self.status_label = tk.Label(self.root, text="F8 开始打字，F9 终止，自动识别剪贴板", fg="gray")
        self.status_label.pack(pady=10)

    def simulate_typing(self):
        text = self.last_clipboard_text.strip()
        if not text:
            self.status_label.config(text="剪贴板为空或无效")
            return
        self.status_label.config(text="正在模拟输入...")
        self.stop_typing_flag = False

        try:
            interval = float(self.typing_interval.get())
            if not (0.005 <= interval <= 1.0):
                raise ValueError
        except ValueError:
            interval = 0.05
            self.typing_interval.set("0.05")
            self.status_label.config(text="间隔值无效，已重置为 0.05")

        time.sleep(0.5)

        if self.mode_var.get() == "快速粘贴":
            pyautogui.write(text)
        else:
            for char in text:
                if self.stop_typing_flag:
                    self.status_label.config(text="输入被终止")
                    return
                pyautogui.write(char)
                time.sleep(interval)

        self.status_label.config(text="输入完成")

    def manual_trigger(self):
        self.typing_thread = threading.Thread(target=self.simulate_typing)
        self.typing_thread.start()

    def start_hotkey_listener(self):
        def hotkey_thread():
            while not self.exit_flag:
                keyboard.wait("F8")
                self.typing_thread = threading.Thread(target=self.simulate_typing)
                self.typing_thread.start()
                keyboard.wait("F9")
                self.stop_typing_flag = True

        threading.Thread(target=hotkey_thread, daemon=True).start()

    def start_clipboard_listener(self):
        def clipboard_monitor():
            while not self.exit_flag:
                try:
                    current = pyperclip.paste()
                    if current and current != self.last_clipboard_text:
                        self.last_clipboard_text = current
                        self.text_box.delete("1.0", tk.END)
                        self.text_box.insert(tk.END, current)
                        self.status_label.config(text="已自动识别并更新剪贴板文本")
                except Exception as e:
                    print(f"剪贴板监听错误: {e}")
                time.sleep(1)

        threading.Thread(target=clipboard_monitor, daemon=True).start()

# 启动程序
if __name__ == "__main__":
    root = tk.Tk()
    app = TypingApp(root)
    root.mainloop()
