import socket
import threading
from datetime import datetime
import sys
import os
import hashlib
clients = []
usernames = {}
time = datetime.now()
ERR = "ERR"
WARN = "WARN"
INFO = "INFO"
CORE = "CORE"
USER = "USER"
CHAT = "CHAT"
def getscriptpath():
    scriptpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    return scriptpath
def calculate_CUUID(file_path, start_line, end_line):
    with open(file_path+"/main.py", 'r') as file:
        lines = file.readlines()
        # Extract the lines between start_line and end_line
        selected_lines = lines[start_line-1:end_line]
        # Concatenate the lines into a single string
        data = ''.join(selected_lines)
        # Compute the checksum using SHA-256
        checksum = hashlib.sha256(data.encode()).hexdigest()
        return checksum
CVUUID = calculate_CUUID(getscriptpath(),0,98)
def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                client.close()
                clients.remove(client)
def format_message(message,type):
    formatted_message = f"[{time} {type}]" + message
    return formatted_message
def handle_client(client_socket,SCVUUID):
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                decoded_message = message.decode('utf-8')
                if decoded_message.startswith("USERNAME:"):
                    username = decoded_message.split(":")[1]
                    usernames[client_socket] = username
                    server_join_message = format_message(f"{username} has joined the chat.",CHAT)
                    print(server_join_message)
                    user_join_message = f"{username} has joined the chat"
                    broadcast(user_join_message.encode('utf-8'))
                elif decoded_message.startswith("/"):
                    handle_command(decoded_message, client_socket)
                elif decoded_message.startwith("CUUID"):
                    client_CVUUID = decoded_message.split(":")[1]
                    if client_CVUUID != SCVUUID:
                        raise ConnectionRefusedError("Incompatible Client")
                else:
                    username = usernames.get(client_socket, "Unknown")
                    broadcast_message = f"{username}: {decoded_message}"
                    print(format_message(broadcast_message,CHAT))
                    broadcast(broadcast_message.encode('utf-8'), client_socket)
            else:
                raise ConnectionResetError("Client disconnected")
        except (ConnectionResetError, ConnectionAbortedError):
            print(format_message(f"Connection closed by {usernames.get(client_socket, 'Unknown')}",USER))
            client_socket.close()
            clients.remove(client_socket)
            break
        except Exception as e:
            print(format_message(f"An error occurred: {e}",ERR))
            client_socket.close()
            clients.remove(client_socket)
            break

def handle_command(command, client_socket):
    if command == "/clients":
        client_list = "\n".join(usernames[client] for client in clients if client in usernames)
        client_socket.send(f"Connected clients:\n{client_list}".encode('utf-8'))

def start_server(host='localhost', port=12345):
    CVUUID = calculate_CUUID(getscriptpath(),0,98)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(format_message(f"initializing Server on {host}:{port}",CORE))
    
    while True:
        client_socket, addr = server_socket.accept()
        print(format_message(f"Connection from {addr}",USER))
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket,CVUUID))
        thread.start()

if __name__ == "__main__":
    start_server()