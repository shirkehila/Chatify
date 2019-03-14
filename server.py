#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time
import queue
from pprint import pprint as pp
import csv

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Greetings from the cave! Now type your name and press enter!", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()



def update_client(client):
    username = clients[client]
    while not users[username].empty():
        client.send(users[username].get())
        time.sleep(0.1)



def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    username = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % username
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % username
    broadcast(bytes(msg, "utf8"))
    clients[client] = username
    update_client(client)

    while True:
        msg = client.recv(BUFSIZ)
        if msg != bytes("{quit}", "utf8"):
            broadcast(msg, username + ": ")
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat." % username, "utf8"))
            print("%s:%s has disconnected." % addresses[client])
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    bytes_msg = bytes(prefix, "utf8") + msg
    for sock in clients:
        sock.send(bytes_msg)
    for user in users:
        if user not in clients:
            users[user].put(bytes_msg)


clients = {}
addresses = {}
users = {}  # a queue to store messages for non connected users
with open('users.csv', mode='r') as f:
    reader = csv.reader(f)
    for user in reader:
        users[user[0]] = queue.Queue()

pp(users)


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