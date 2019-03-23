#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import pickle
import os.path
from tkinter import filedialog
import time
import ntpath
from math import ceil
from tkinter import ttk
from directory import DirTree
from sign_up_in import MyApp

online = False
cur_username = ""

def change_uname(uname):
    global cur_username
    cur_username = uname


def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg_list.insert(tkinter.END, msg)
            msg_list.yview(tkinter.END)
            save_history()
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    # if client is connecting
    global online
    global username
    msg = my_msg.get()
    if online and msg != '{quit}':
        msg = '{text}' + msg
    if not online:
        online = True
        username = my_msg.get()  # set username global variable
        load_history()
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        # save_history()
        client_socket.close()
        root.quit()


def send_file(event=None):
    filename = filedialog.askopenfilename()
    filesize = os.path.getsize(filename)
    CHUNK_SIZE = 1024
    chunks = ceil(filesize/CHUNK_SIZE)
    msg = '{file}' + ntpath.basename(filename) + '|'+str(chunks)
    client_socket.send(bytes(msg,'utf8'))
    print(str(chunks))
    time.sleep(1)

    with open(filename, 'rb') as f:
        chunk = f.read(CHUNK_SIZE)
        while (chunk):
            client_socket.send(chunk, 0)
            chunk = f.read(CHUNK_SIZE)


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


root = tkinter.Tk()
note = ttk.Notebook(root)
chat_tab = ttk.Frame(note)
files_tab = ttk.Frame(note)
root.title("Chatter")

messages_frame = tkinter.Frame(chat_tab)
my_msg = tkinter.StringVar()  # For the messages to be sent.
#my_msg.configure(state=tkinter.DISABLED)
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=60, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

path_to_my_project = r"files"
app = DirTree(files_tab, path=path_to_my_project)


bottom_frame = tkinter.Frame(chat_tab)
entry_field = tkinter.Entry(bottom_frame, width=40, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack(side=tkinter.LEFT)
send_button = tkinter.Button(bottom_frame, text="Send", command=send)
send_button.pack(side=tkinter.LEFT)
send_file_button = tkinter.Button(bottom_frame, text="Send File", command=send_file)
send_file_button.pack(side=tkinter.LEFT)
bottom_frame.pack()

note.add(chat_tab, text='chat')
note.add(files_tab, text='files')
note.pack()
root.protocol("WM_DELETE_WINDOW", on_closing)


sign = MyApp()
sign.run()
cur_username = sign.get_username()
if cur_username == "":
    exit()
my_msg.set(cur_username)



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
send()
tkinter.mainloop()  # Starts GUI execution.