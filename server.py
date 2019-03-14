#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time
import collections
from pprint import pprint as pp
import csv
import pickle


def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def update_client(client):
    """Send the client all the messages he missed"""
    username = clients[client]
    while users[username]:
        client.send(users[username].popleft())
        time.sleep(0.1)


def get_req_msg(request):
    """Given a request, the method finds the type of request and msg"""
    # convert from bytes
    request = request.decode("utf8")
    end_type = request.index('}')
    req_type = request[:end_type+1]
    msg = request[end_type+1:]
    return req_type, bytes(msg,"utf8")


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    username = client.recv(BUFSIZ).decode("utf8")
    clients[client] = username
    update_client(client)

    while True:
        request = client.recv(BUFSIZ)
        req_type, msg = get_req_msg(request)
        if req_type == "{text}":
            broadcast(msg, username + ": ")
        elif req_type == "{quit}":
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            print("%s:%s has disconnected." % addresses[client])
            break
        elif req_type == "{file}":
            CHUNK_SIZE = 8 * 1024
            # here msg holds file name
            with open("files\{}".format(msg.decode('utf8')), 'wb') as f:
                chunk = client.recv(CHUNK_SIZE)
                f.write(chunk)
                while chunk:
                    chunk = client.recv(CHUNK_SIZE)
                    f.write(chunk)



def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    bytes_msg = bytes(prefix, "utf8") + msg
    for sock in clients:
        sock.send(bytes_msg)
    for user in users:
        if user not in clients.values():
            users[user].append(bytes_msg)
    with open("users_replica.p","wb") as urf:
        pickle.dump(users,urf)


clients = {}
addresses = {}
users = {}  # a queue to store messages for non connected users


with open("users_replica.p","rb") as urf:
    users = pickle.load(urf)


HOST = '127.0.0.1'
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
