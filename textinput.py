"""Среднее задание 2. Вывод текста из поля ввода."""
import tkinter as tk
from tkinter import ttk


def main():
    root = tk.Tk()
    root.title("Ввод текста")
    root.geometry("400x170")

    ttk.Label(root, text="Введите текст:").pack(pady=(15, 5))
    entry = ttk.Entry(root, width=40)
    entry.pack(pady=5)
    output = tk.StringVar(value="Здесь появится ваш текст")
    ttk.Label(root, textvariable=output, wraplength=360).pack(pady=5)

    def show_text():
        output.set(entry.get())

    ttk.Button(root, text="Вывести текст", command=show_text).pack(pady=5)
    entry.bind("<Return>", lambda event: show_text())
    entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()
