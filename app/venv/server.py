import threading
import socket
from User import User

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
users = []
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = set()
clients_lock = threading.Lock()


def handle_client(user):
    client = user.client
    addr = user.addr
    name = user.name = client.recv(1024).decode(FORMAT)
    print(f"[{name}] {addr} Connected")

    try:
        connected = True
        while connected:
            msg = client.recv(1024).decode(FORMAT)
            if not msg:
                break
            if msg == "userlist":
                print(users)

            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{name}] {msg}")
            with clients_lock:
                for c in clients:
                    c.sendall(f"[{name}] {msg}".encode(FORMAT))

    finally:
        with clients_lock:
            clients.remove(client)
            users.remove(user)

        client.close()


def start():
    print('[SERVER STARTED]!')
    server.listen()
    while True:
        client, addr = server.accept()
        with clients_lock:
            user = User(addr, client)
            users.append(user)
            clients.add(user.client)
        thread = threading.Thread(target=handle_client, args=(user, ))
        thread.start()


start()
