import socket
import threading

clients = []
usernames = {}

def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                client.close()
                clients.remove(client)

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                decoded_message = message.decode('utf-8')
                if decoded_message.startswith("USERNAME:"):
                    username = decoded_message.split(":")[1]
                    usernames[client_socket] = username
                    join_message = f"{username} has joined the chat."
                    print(join_message)
                    broadcast(join_message.encode('utf-8'))
                else:
                    username = usernames.get(client_socket, "Unknown")
                    broadcast_message = f"{username}: {decoded_message}"
                    print(broadcast_message)
                    broadcast(broadcast_message.encode('utf-8'), client_socket)
            else:
                client_socket.close()
                clients.remove(client_socket)
                break
        except:
            client_socket.close()
            clients.remove(client_socket)
            break

def start_server(host='localhost', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    start_server()
