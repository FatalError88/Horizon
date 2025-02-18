import socket
import tkinter as tk
from tkinter import scrolledtext, simpledialog, filedialog
import threading
import os 
import io
import winsound
import shutil
import json
from datetime import datetime

HorizonConfig = f"C:/Users/{os.getlogin()}/HorizonConfig/"
HorizonConfigFile = f"{HorizonConfig}config.conf"
NotificationSoundFile = f"{HorizonConfig}notification.wav"
SystemUsername = os.getlogin()

class ChatClient:
    def __init__(self, master):
        self.setup_config()
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

        self.select_sound_button = tk.Button(master, text="Select Notification Sound", command=self.select_sound)
        self.select_sound_button.pack(pady=5)

        self.client_socket = None
        self.username = None

    def setup_config(self):
        if not os.path.exists(HorizonConfig):
            os.makedirs(HorizonConfig)
        if not os.path.exists(HorizonConfigFile):
            with io.open(HorizonConfigFile, "w") as file:
                username = simpledialog.askstring("Username", "Enter your username:")
                file.write(f"Username={username}\n")

    def connect_to_server(self):
        host = simpledialog.askstring("Server Address", "Enter the server IP address:", initialvalue='localhost')
        port = simpledialog.askinteger("Server Port", "Enter the server port:", initialvalue=12345, minvalue=1, maxvalue=65535)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        try:
            self.client_socket.connect((host, port))
            with open(HorizonConfigFile, "r") as config_file:
                self.username = config_file.read().split("=")[1].strip()
            self.send_horizon_message('USERNAME', self.username)
            
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
                    horizon_message = json.loads(message)
                    self.display_message(f"{horizon_message['content']}")
                    if os.path.exists(NotificationSoundFile):
                        winsound.PlaySound(NotificationSoundFile, winsound.SND_FILENAME)
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
                if message.startswith('/'):
                    self.send_horizon_message('COMMAND', message)
                else:
                    self.send_horizon_message('MESSAGE', message)
                self.display_message(f"{self.username}: {message}")
                self.msg_entry.delete(0, tk.END)
            except (ConnectionResetError, ConnectionAbortedError):
                self.display_message("Connection closed by the server.")
            except BrokenPipeError:
                self.display_message("Broken pipe error. You might need a plumber =P")
            except Exception as e:
                self.display_message(f"An error occurred: {e}")

    def send_horizon_message(self, msg_type, content):
        message = {
            'type': msg_type,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self.client_socket.send(json.dumps(message).encode('utf-8'))

    def display_message(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message + '\n')
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def select_sound(self):
        file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if file_path:
            try:
                shutil.copy(file_path, NotificationSoundFile)
                self.display_message("Notification sound updated successfully.")
            except Exception as e:
                self.display_message(f"Error updating notification sound: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    client.connect_to_server()
    root.mainloop()