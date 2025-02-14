import socket
import tkinter as tk
from tkinter import scrolledtext, simpledialog
import threading

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Horizon Client")
        self.master.geometry("400x500")

        self.chat_display = scrolledtext.ScrolledText(master, state='disabled')
        self.chat_display.pack(padx=10, pady=10, expand=True, fill='both')

        self.msg_entry = tk.Entry(master)
        self.msg_entry.pack(padx=10, pady=5, fill='x')
        self.msg_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

        self.client_socket = None
        self.username = None

    def connect_to_server(self):
        host = simpledialog.askstring("Server Address", "Enter the server IP address:", initialvalue='localhost')
        port = simpledialog.askinteger("Server Port", "Enter the server port:", initialvalue=12345, minvalue=1, maxvalue=65535)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        try:
            self.client_socket.connect((host, port))
            self.username = simpledialog.askstring("Username", "Enter your username:")
            self.client_socket.send(f"USERNAME:{self.username}".encode('utf-8'))
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
        except Exception as e:
            self.display_message(f"Failed to connect: {e}")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.display_message(message)
                else:
                    raise ConnectionResetError("Server closed the connection")
            except (ConnectionResetError, ConnectionAbortedError):
                self.display_message("Connection closed by the server.")
                break
            except Exception as e:
                self.display_message(f"An error occurred: {e}")
                break

    def send_message(self, event=None):
        message = self.msg_entry.get()
        if message:
            try:
                self.client_socket.send(message.encode('utf-8'))
                self.display_message(f"{self.username}: {message}")  # Display own message
                self.msg_entry.delete(0, tk.END)
            except (ConnectionResetError, ConnectionAbortedError):
                self.display_message("Connection closed by the server.")
            except BrokenPipeError:
                self.display_message("Broken pipe error. You might need a plumber =P")
            except Exception as e:
                self.display_message(f"An error occurred: {e}")

    def display_message(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message + '\n')
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    client.connect_to_server()
    root.mainloop()