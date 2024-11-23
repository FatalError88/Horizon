import socket
import threading
from win10toast import ToastNotifier
import os
import importlib.util
import hashlib
import sys
toasts = ToastNotifier()
def getscriptpath():
    scriptpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    return scriptpath
def calculate_CUUID(file_path, start_line, end_line):
    with open(file_path+"/client.py", 'r') as file:
        lines = file.readlines()
        # Extract the lines between start_line and end_line
        selected_lines = lines[start_line-1:end_line]
        # Concatenate the lines into a single string
        data = ''.join(selected_lines)
        # Compute the checksum using SHA-256
        checksum = hashlib.sha256(data.encode()).hexdigest()
        return checksum
CVUUID =  "e"#calculate_CUUID(getscriptpath(),0,87)

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                try:
                    toasts.show_toast("Horizon", message, duration=10)
                    print(message)
                except TypeError:
                    pass

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
            #wait for message input and sends it
            message = input(">")
            client_socket.send(message.encode('utf-8'))
            #error handling
        except (ConnectionResetError, ConnectionAbortedError):
            print("Connection closed by the server.")
            break
        except BrokenPipeError:
            print("Broken pipe error. you might need a plumber =P")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

def start_client(host='localhost', port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE, 1)
    client_socket.connect((host, port))
    #asks for the username
    username = input("Enter your username: ")
    client_socket.send(f"USERNAME:{username}".encode('utf-8'))
    client_socket.send(("ccuid:" + CVUUID).encode("utf-8")) 
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))
    send_thread.daemon = True
    send_thread.start()

    receive_thread.join()
    send_thread.join()

if __name__ == "__main__":
    #ask for the IP or DNS of the server
    host = input("Enter the server IP address (default 'localhost'): ") or 'localhost'
    #ask for the  port of the server
    port = int(input("Enter the server port (default 12345): ") or 12345)
    #... guess what this does
    start_client(host, port)
