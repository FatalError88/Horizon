import socket
import threading
from win10toast import ToastNotifier
import os
import importlib.util 

toasts = ToastNotifier()
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                toasts.show_toast("Horizon", message, duration=10)
                print(message)

            else:
                raise ConnectionResetError("Server closed the connection")
        except (ConnectionResetError, ConnectionAbortedError):
            print("Connection closed by the server.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

def send_messages(client_socket):
    while True:
        try:
            message = input(">")
            client_socket.send(message.encode('utf-8'))
        except (ConnectionResetError, ConnectionAbortedError):
            print("Connection closed by the server.")
            break
        except BrokenPipeError:
            print("Broken pipe error. Connection lost.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

def start_client(host='localhost', port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    client_socket.connect((host, port))
    username = input("Enter your username: ")
    client_socket.send(f"USERNAME:{username}".encode('utf-8'))
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))
    send_thread.daemon = True
    send_thread.start()

    receive_thread.join()
    send_thread.join()

if __name__ == "__main__":
    host = input("Enter the server IP address (default 'localhost'): ") or 'localhost'
    port = int(input("Enter the server port (default 12345): ") or 12345)
    start_client(host, port)
