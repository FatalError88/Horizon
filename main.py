import socket
import threading
import json
from datetime import datetime 
import os
import io
import hashlib
import secrets

HorizonConfig = f"C:/Users/{os.getlogin()}/HorizonServerConfig/"
HorizonConfigFile = f"{HorizonConfig}config.conf"
SystemUsername = os.getlogin()
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
clients = []
usernames = {}

ERR, WARN, INFO, CORE, USER, CHAT = "ERR", "WARN", "INFO", "CORE", "USER", "CHAT"

def setup_config():
    if not os.path.exists(HorizonConfig):
        os.makedirs(HorizonConfig)
    if not os.path.exists(HorizonConfigFile):
        with io.open(HorizonConfigFile, "w") as file:
            port = input("Input Server Port (can be changed in the config): ")
            file.write(f"Port={port}")

def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(json.dumps(message).encode('utf-8'))
            except:
                client.close()
                clients.remove(client)

def format_message(message, type):
    return {"timestamp": datetime.now().isoformat(), "type": type, "content": message}

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                decoded_message = json.loads(message.decode('utf-8'))
                if decoded_message['type'] == 'USERNAME':
                    username = decoded_message['content']
                    usernames[client_socket] = username
                    ServerLog(f"{username} has joined the chat", USER)
                    broadcast(format_message(f"{username} has joined the chat", USER))
                elif decoded_message['type'] == 'COMMAND':
                    handle_command(decoded_message['content'], client_socket)
                elif decoded_message['type'] == 'MESSAGE':
                    username = usernames.get(client_socket, "Unknown")
                    broadcast_message = f"{username}: {decoded_message['content']}"
                    ServerLog(broadcast_message, CHAT)
                    broadcast(format_message(broadcast_message, CHAT), client_socket)
            else:
                raise ConnectionResetError("Client disconnected")
        except (ConnectionResetError, ConnectionAbortedError):
            username = usernames.get(client_socket, "Unknown")
            ServerLog(f"Connection closed by {username}", USER)
            client_socket.close()
            clients.remove(client_socket)
            break
        except Exception as e:
            ServerLog(f"An error occurred: {e}", ERR)
            client_socket.close()
            clients.remove(client_socket)
            break

def handle_command(command, client_socket):
    if command == "/clients":
        client_list = "\n".join(usernames[client] for client in clients if client in usernames)
        client_socket.send(json.dumps(format_message(f"Connected clients:\n{client_list}", INFO)).encode('utf-8'))
    elif command == "/stop":
        ServerLog("Server is shutting down.", CORE)
        broadcast(format_message("Server is shutting down.", CORE))
        for client in clients:
            client.close()
        os._exit(0)

def ServerLog(message, msgtype):
    print(json.dumps(format_message(message, msgtype)))

def start_server(ip_address):
    setup_config()
    with open(HorizonConfigFile, "r") as config_file:
        port = int(config_file.read().split("=")[1])
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip_address, port))
    server_socket.listen(5)
    ServerLog(f"Initializing Server on {ip_address}:{port}", CORE)
    
    while True:
        client_socket, addr = server_socket.accept()
        ServerLog(f"Connection from {addr}", USER)
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    start_server(ip_address)