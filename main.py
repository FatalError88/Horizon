import asyncio
import websockets

clients = []
usernames = {}

async def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                await client.send(message)
            except:
                await client.close()
                clients.remove(client)

async def handle_client(websocket, path):
    clients.append(websocket)
    try:
        async for message in websocket:
            if message.startswith("USERNAME:"):
                username = message.split(":")[1]
                usernames[websocket] = username
                join_message = f"{username} has joined the chat."
                print(join_message)
                await broadcast(join_message, websocket)
            else:
                username = usernames.get(websocket, "Unknown")
                broadcast_message = f"{username}: {message}"
                print(broadcast_message)
                await broadcast(broadcast_message, websocket)
    except:
        clients.remove(websocket)

async def start_server():
    server = await websockets.serve(handle_client, 'localhost', 12345)
    print("Server listening on localhost:12345")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(start_server())

