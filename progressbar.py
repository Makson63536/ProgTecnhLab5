"""Среднее задание 6. Демонстрация прогрессбара."""
import tkinter as tk
from tkinter import ttk


def main():
    root = tk.Tk()
    root.title("Прогрессбар")
    root.geometry("360x150")
    root.resizable(False, False)

    value = tk.IntVar(value=0)
    ttk.Label(root, text="Выполнение задачи:").pack(pady=(15, 5))
    bar = ttk.Progressbar(root, maximum=100, variable=value, length=280)
    bar.pack(pady=5)
    status = ttk.Label(root, text="0%")
    status.pack()
    start_button = ttk.Button(root, text="Запустить")
    start_button.pack(pady=8)

    def step():
        value.set(min(value.get() + 1, 100))
        status.config(text=f"{value.get()}%")
        if value.get() < 100:
            root.after(50, step)
        else:
            start_button.config(state="normal", text="Запустить снова")

    def start():
        value.set(0)
        status.config(text="0%")
        start_button.config(state="disabled")
        step()

    start_button.config(command=start)
    root.mainloop()


if __name__ == "__main__":
    main()
