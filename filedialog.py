"""Среднее задание 8. Диалог выбора файла."""
import tkinter as tk
from tkinter import filedialog, ttk


def main():
    root = tk.Tk()
    root.title("Выбор файла")
    root.geometry("500x160")

    path = tk.StringVar(value="Файл не выбран")
    ttk.Label(root, text="Нажмите кнопку и выберите файл:").pack(pady=(18, 8))
    ttk.Label(root, textvariable=path, wraplength=460).pack(pady=5)

    def choose_file():
        selected = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[("Все файлы", "*.*"), ("Текстовые файлы", "*.txt")],
        )
        if selected:
            path.set(selected)

    ttk.Button(root, text="Выбрать файл", command=choose_file).pack(pady=10)
    root.mainloop()


if __name__ == "__main__":
    main()
