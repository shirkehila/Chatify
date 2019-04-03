#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time
import collections
from pprint import pprint as pp
import csv
import pickle
from classify import Classifier
import os
from listdir import DirAsXML

username = ""
cur_path = ""


model_path = 'news20.gensim'
dict_name = 'dictionary20'
c = Classifier(model_path, dict_name)


def move_file(cur_path, new_path):
    """move file from old path to new path"""
    try:
        os.rename(cur_path, new_path)
    except FileExistsError:
        filename, file_extension = os.path.splitext(new_path)
        new_path=filename+"(1)"+file_extension
        move_file(cur_path, new_path)


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
    req_type = request[:end_type + 1]
    msg = request[end_type + 1:]
    return req_type, bytes(msg, "utf8")


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    username = client.recv(BUFSIZ).decode("utf8")
    clients[client] = username
    if username not in users:
        users[username] = collections.deque()
        with open("users_replica.p", "wb") as urf:
            pickle.dump(users, urf)
    else:
        update_client(client)

    while True:
        request = client.recv(BUFSIZ)
        req_type, msg = get_req_msg(request)
        if req_type == "{text}":
            broadcast(msg, username + ": ")
        elif req_type == "{quit}":
            try:
                client.send(bytes("{quit}", "utf8"))
            except ConnectionResetError as e:
                print(e)

            client.close()
            del clients[client]
            print("%s:%s has disconnected." % addresses[client])
            break
        elif req_type == "{file}":
            CHUNK_SIZE = 1 * 1024
            # here msg holds file name
            msg_parts = msg.decode('utf8').split('|')
            filename = msg_parts[0]
            name, extension = os.path.splitext(filename)

            broadcast(bytes("{} has sent file: {}".format(clients[client], filename), 'utf8'))
            with open("files\{}".format(filename), 'wb') as f:
                for i in range(int(msg_parts[1])):
                    # print('receiving data...')
                    data = client.recv(CHUNK_SIZE)
                    if not data:
                        break
                    # write data to a file
                    f.write(data)
            if extension == '.txt':
                unicast(client, bytes("sending classes", 'utf-8'), "{class}")
                global cur_path
                cur_path = "files\{}".format(filename, 'rt')
                with open(cur_path) as tf:
                    line = tf.readline()
                    print(line)
                    text = ""
                    while line:
                        text += line
                        line = tf.readline()
                        print(line)
                response = c.class_and_words(text)
                client.send(pickle.dumps(response))
        elif req_type == "{ok}":
            # client agrees to the classification
            msg = msg.decode('utf-8')
            cur_dir = os.path.dirname(cur_path)
            base_name = os.path.basename(cur_path)
            new_dir = os.path.join(cur_dir,msg)
            new_path = os.path.join(new_dir,base_name)
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            move_file(cur_path, new_path)

        elif req_type == "{tree}":
            msg = bytes(DirAsXML('files'), encoding='utf-8')
            unicast(client,msg, "{tree}")

        elif req_type == "{download}":
            path = os.path.join("files",msg.decode('utf-8'))
            fsize = os.path.getsize(path)
            unicast(client,bytes(str(fsize),'utf-8'),"{download}")
            CHUNK_SIZE = 1024
            print(path)
            with open(path, 'rb') as f:
                chunk = f.read(CHUNK_SIZE)
                while chunk:
                    client.send(chunk, 0)
                    chunk = f.read(CHUNK_SIZE)
                print("done")


def broadcast(msg, prefix="", req_type="{text}"):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    bytes_msg = bytes(req_type + prefix, "utf8") + msg
    for sock in clients:
        sock.send(bytes_msg)
    for user in users:
        if user not in clients.values():
            users[user].append(bytes_msg)
    with open("users_replica.p", "wb") as urf:
        pickle.dump(users, urf)


def unicast(client, msg, req_type="{text}"):
    """Unicasts a message to a clients."""
    bytes_msg = bytes(req_type, "utf8") + msg
    client.send(bytes_msg)


clients = {}
addresses = {}
users = {}  # a queue to store messages for non connected users



HOST = '127.0.0.1'
PORT = 33000
BUFSIZ = 1024*8
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    with open("users_replica.p", "rb") as urf:
        users = pickle.load(urf)
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
