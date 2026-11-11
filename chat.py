"""Повышенное задание 10. Локальный чат на TCP и Tkinter."""
import queue
import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

HOST = "127.0.0.1"
PORT = 50505
MAX_LINE = 4096


class ChatServer:
    """Сервер принимает клиентов на этом компьютере и пересылает сообщения."""

    def __init__(self):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.listener.bind((HOST, PORT))
            self.listener.listen()
        except OSError:
            self.listener.close()
            raise
        self.clients = set()
        self.lock = threading.Lock()
        self.running = True

    def start(self):
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        while self.running:
            try:
                client, _ = self.listener.accept()
            except OSError:
                break
            with self.lock:
                if not self.running:
                    client.close()
                    break
                self.clients.add(client)
            threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()

    def handle_client(self, client):
        try:
            with client.makefile("rb") as stream:
                while self.running:
                    line = stream.readline(MAX_LINE + 1)
                    if not line or len(line) > MAX_LINE or not line.endswith(b"\n"):
                        break
                    # Клиенты передают UTF-8, одно сообщение — одна строка.
                    line.decode("utf-8")
                    with self.lock:
                        for other in list(self.clients):
                            try:
                                other.sendall(line)
                            except OSError:
                                self.clients.discard(other)
                                other.close()
        except (OSError, UnicodeError):
            pass
        finally:
            with self.lock:
                self.clients.discard(client)
            client.close()

    def close(self):
        self.running = False
        self.listener.close()
        with self.lock:
            clients = list(self.clients)
            self.clients.clear()
        for client in clients:
            try:
                client.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            client.close()


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.server = None
        self.client = None
        self.events = queue.Queue()
        self.root.title("Локальный чат")
        self.root.geometry("650x500")
        self.root.minsize(500, 350)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        top = ttk.Frame(root, padding=8)
        top.pack(fill=tk.X)
        ttk.Label(top, text="Имя:").pack(side=tk.LEFT)
        self.name = ttk.Entry(top, width=16)
        self.name.insert(0, "Участник")
        self.name.pack(side=tk.LEFT, padx=5)
        self.start_button = ttk.Button(top, text="Создать сервер", command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=3)
        self.connect_button = ttk.Button(top, text="Подключиться", command=self.connect)
        self.connect_button.pack(side=tk.LEFT, padx=3)

        self.status = tk.StringVar(value=f"Не подключено. Сервер: {HOST}:{PORT}")
        ttk.Label(root, textvariable=self.status).pack(anchor=tk.W, padx=8)
        # Нижнюю панель размещаем первой, чтобы история не вытеснила её из окна.
        bottom = ttk.Frame(root, padding=(8, 0, 8, 8))
        bottom.pack(side=tk.BOTTOM, fill=tk.X)
        self.history = scrolledtext.ScrolledText(
            root, state="disabled", wrap=tk.WORD, height=10
        )
        self.history.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.message = ttk.Entry(bottom)
        self.message.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message.bind("<Return>", lambda event: self.send())
        self.send_button = ttk.Button(bottom, text="Отправить", command=self.send, state="disabled")
        self.send_button.pack(side=tk.LEFT, padx=(5, 0))
        self.root.after(100, self.poll_events)

    def start_server(self):
        try:
            self.server = ChatServer()
            self.server.start()
        except OSError as error:
            messagebox.showerror("Ошибка сервера", f"Не удалось запустить сервер: {error}")
            return
        self.start_button.config(state="disabled")
        self.status.set("Сервер запущен. Подключитесь к нему.")
        self.connect()

    def connect(self):
        if self.client is not None:
            return
        name = self.name.get().strip()
        if not name:
            messagebox.showwarning("Имя", "Введите имя участника.")
            return
        try:
            client = socket.create_connection((HOST, PORT), timeout=2)
            client.settimeout(None)
        except OSError as error:
            messagebox.showerror("Ошибка подключения", f"Сначала запустите сервер.\n{error}")
            return
        self.client = client
        self.name.config(state="disabled")
        self.start_button.config(state="disabled")
        self.connect_button.config(state="disabled")
        self.send_button.config(state="normal")
        self.status.set(f"Подключено к {HOST}:{PORT}")
        self.message.focus_set()
        threading.Thread(target=self.receive, args=(client,), daemon=True).start()

    def receive(self, client):
        try:
            with client.makefile("rb") as stream:
                while True:
                    line = stream.readline(MAX_LINE + 1)
                    if not line or len(line) > MAX_LINE or not line.endswith(b"\n"):
                        break
                    self.events.put(("message", line.decode("utf-8").rstrip("\n")))
        except (OSError, UnicodeError):
            pass
        finally:
            self.events.put(("disconnected", "Соединение закрыто. Перезапустите программу."))

    def send(self):
        text = self.message.get().strip()
        if not text or self.client is None:
            return
        line = f"{self.name.get()}: {text}\n".encode("utf-8")
        if len(line) > MAX_LINE:
            messagebox.showwarning("Сообщение", "Сообщение слишком длинное.")
            return
        try:
            self.client.sendall(line)
            self.message.delete(0, tk.END)
        except OSError:
            self.status.set("Ошибка отправки. Перезапустите программу.")
            self.send_button.config(state="disabled")

    def poll_events(self):
        while True:
            try:
                kind, text = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == "message":
                self.history.config(state="normal")
                self.history.insert(tk.END, text + "\n")
                self.history.see(tk.END)
                self.history.config(state="disabled")
            else:
                self.status.set(text)
                self.send_button.config(state="disabled")
        self.root.after(100, self.poll_events)

    def close(self):
        if self.client:
            try:
                self.client.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.client.close()
        if self.server:
            self.server.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    ChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
