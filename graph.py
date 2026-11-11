"""Повышенное задание 4. График matplotlib внутри Tkinter."""
import math
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def main():
    root = tk.Tk()
    root.title("График внутри Tkinter")
    root.geometry("700x500")

    figure = Figure(figsize=(6, 4), dpi=100)
    axes = figure.add_subplot(111)
    x_values = [i / 10 for i in range(-100, 101)]
    line, = axes.plot(x_values, [math.sin(x) for x in x_values])
    axes.set_title("График y = sin(x)")
    axes.set_xlabel("x")
    axes.set_ylabel("y")
    axes.grid(True)
    figure.tight_layout()

    canvas = FigureCanvasTkAgg(figure, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def change_graph(event=None):
        if choice.get() == "sin(x)":
            y_values = [math.sin(x) for x in x_values]
        else:
            y_values = [math.cos(x) for x in x_values]
        line.set_ydata(y_values)
        axes.set_title(f"График y = {choice.get()}")
        canvas.draw_idle()

    panel = ttk.Frame(root)
    panel.pack(pady=8)
    ttk.Label(panel, text="Функция:").pack(side=tk.LEFT, padx=5)
    choice = ttk.Combobox(panel, values=["sin(x)", "cos(x)"], state="readonly", width=10)
    choice.current(0)
    choice.pack(side=tk.LEFT)
    choice.bind("<<ComboboxSelected>>", change_graph)
    root.mainloop()


if __name__ == "__main__":
    main()
