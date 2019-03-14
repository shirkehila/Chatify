#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import pickle
import os.path
from tkinter import filedialog

online = False
username = ''


def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg_list.insert(tkinter.END, msg)
            save_history()
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    # if client is connecting
    global online
    global username
    if not online:
        online = True
        username = my_msg.get()  # set username global variable
        load_history()
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        # save_history()
        client_socket.close()
        top.quit()


def send_file(event=None):
    filename = filedialog.askopenfilename()
    # my_msg.set(filename)


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    # save_history()
    my_msg.set("{quit}")
    send()


def save_history():
    """save history listbox using pickle"""
    global username
    if username == '':
        return
    with open('{}_history.p'.format(username), 'wb') as hf:
        history = msg_list.get(0, tkinter.END)
        pickle.dump(history,hf)


def load_history():
    """load history to listbox using pickle"""
    global username
    hist_path = '{}_history.p'.format(username)
    if os.path.isfile(hist_path):
        with open(hist_path, 'rb') as hf:
            history = pickle.load(hf)
            for msg in history:
                msg_list.insert(tkinter.END, msg)


top = tkinter.Tk()
top.title("Chatter")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("Enter username")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=60, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

bottom_frame = tkinter.Frame(top)
entry_field = tkinter.Entry(bottom_frame, width=40, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack(side=tkinter.LEFT)
send_button = tkinter.Button(bottom_frame, text="Send", command=send)
send_button.pack(side=tkinter.LEFT)
send_file_button = tkinter.Button(bottom_frame, text="Send File", command=send_file)
send_file_button.pack(side=tkinter.LEFT)
bottom_frame.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

#----Now comes the sockets part----
HOST = '127.0.0.1'
PORT = ''
if not PORT:
    PORT = 33000
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.
