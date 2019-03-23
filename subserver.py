#!/usr/bin/env python3

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from sqllite_ import DB

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


def handle_clients():
    while True:
        conn, addr = SERVER.accept()
        with conn:
            print('Connected by', addr)
            data = conn.recv(1024)
            data_dec = data.decode("utf8")
            req_type, content = tuple(data_dec.split('|'))
            req_type = int(req_type)
            if 1 <= req_type <= 2:
                content = content.split(";")
                username = content[0]
                password = content[1]
                response = -2
                if req_type == 1:
                    response = str(db.check_user_pass(username, password))
                elif req_type == 2:
                    if db.user_exists(username):
                        response = 0
                    else:
                        db.add_user(username, password)
                        response = 1
                response = str(response)
                conn.sendall(bytes(response, encoding="utf-8"))


BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    db = DB()
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=handle_clients)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
