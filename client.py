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
from bar import Bar

online = False
cur_username = ""
cur_path = ""


def popup(data, topic, words):
    def clicked_ok():
        print("ok")
        request("{ok}",str(topic))
        win.destroy()

    def clicked_cancel():
        print("cancel")
        win.destroy()
    win = tkinter.Toplevel()
    win.wm_title("Classification")
    vals = [x[1] for x in data]

    bar = Bar(win, data, topic, words)

    bar.grid(row=0, column=0)
    btns = tkinter.Frame(win)
    ok = ttk.Button(btns, text="Okay", command=clicked_ok)
    ok.grid(row=0, column=0)
    cancel = ttk.Button(btns, text="Cancel", command=clicked_cancel)
    cancel.grid(row=0, column=1)
    btns.grid(row=1, column=0)


def get_req_msg(request):
    """Given a request, the method finds the type of request and msg"""
    # convert from bytes
    request = request.decode("utf8")
    end_type = request.index('}')
    req_type = request[:end_type + 1]
    msg = request[end_type + 1:]
    return req_type, msg


def receive():
    """Handles receiving of messages."""
    while True:
        try:
            req = client_socket.recv(BUFSIZ)
            req_type, msg = get_req_msg(req)
            if req_type == "{text}":
                msg_list.insert(tkinter.END, msg)
                msg_list.yview(tkinter.END)
                save_history()
            elif req_type == "{tree}":
                app.process_xml(msg)
            elif req_type == "{class}":
                #server sends recommendation for classification
                dmp = client_socket.recv(BUFSIZ)
                classif = pickle.loads(dmp)
                popup(classif[0], classif[1], classif[2])
            elif req_type == "{download}":
                global cur_path
                filename = os.path.basename(cur_path)
                CHUNK_SIZE = 1 * 1024
                file_size= int(msg)
                parts = ceil(file_size / CHUNK_SIZE)
                file_path = os.path.join(cur_username, filename)
                if not os.path.exists(cur_username):
                    os.makedirs(cur_username)
                with open(file_path, 'wb') as f:
                    for i in range(parts):
                        print('receiving data...')
                        data = client_socket.recv(CHUNK_SIZE)
                        if not data:
                            break
                        # write data to a file
                        f.write(data)
        except OSError:  # Possibly client has left the chat.
            break


def request(req_type, msg=""):
    client_socket.send(bytes(req_type+msg, "utf8"))


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    # if client is connecting
    global online
    global username
    msg = my_msg.get()
    if online and msg != '{quit}' and msg !="":
        request("{text}", msg)
    if not online:
        online = True
        username = my_msg.get()  # set username global variable
        load_history()
        request("",msg)
    my_msg.set("")  # Clears input field.
    if msg == "{quit}":
        request("", msg)
        # save_history()
        client_socket.close()
        root.quit()


def send_file(event=None):
    filename = filedialog.askopenfilename()
    filesize = os.path.getsize(filename)
    CHUNK_SIZE = 1024
    chunks = ceil(filesize / CHUNK_SIZE)
    msg = '{file}' + ntpath.basename(filename) + '|' + str(chunks)
    client_socket.send(bytes(msg, 'utf8'))
    print(str(chunks))
    time.sleep(1)

    with open(filename, 'rb') as f:
        chunk = f.read(CHUNK_SIZE)
        while chunk:
            client_socket.send(chunk, 0)
            chunk = f.read(CHUNK_SIZE)



def download():
    path = app.get_selected_path()
    if path:
        request("{download}",path)
        global cur_path
        cur_path = path




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
        pickle.dump(history, hf)


def load_history():
    """load history to listbox using pickle"""
    global username
    hist_path = '{}_history.p'.format(username)
    if os.path.isfile(hist_path):
        with open(hist_path, 'rb') as hf:
            history = pickle.load(hf)
            for msg in history:
                msg_list.insert(tkinter.END, msg)


def load_tree():
    request("{tree}")


root = tkinter.Tk()
note = ttk.Notebook(root)
chat_tab = ttk.Frame(note)
files_tab = ttk.Frame(note)
root.title("Chatter")

messages_frame = tkinter.Frame(chat_tab)
my_msg = tkinter.StringVar()  # For the messages to be sent.
# my_msg.configure(state=tkinter.DISABLED)
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=60, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

path_to_my_project = r"files"
tree_frame = tkinter.Frame(files_tab)
app = DirTree(tree_frame)
tree_frame.pack()
btns_frame = tkinter.Frame(files_tab)
get_tree_button = tkinter.Button(btns_frame, text="Load Tree", command=load_tree)
get_tree_button.pack(side=tkinter.LEFT)
download_button = tkinter.Button(btns_frame, text="Download", command=download)
download_button.pack(side=tkinter.LEFT)
btns_frame.pack()


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

# ----Now comes the sockets part----
HOST = '127.0.0.1'
PORT = 33000

BUFSIZ = 1024*8

ADDR = (HOST, PORT)

if __name__ == "__main__":
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)

    receive_thread = Thread(target=receive)
    receive_thread.start()
    send()
    tkinter.mainloop()  # Starts GUI execution.
