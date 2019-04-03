#!/usr/bin/env python3

import socket


class DBC:
    def __init__(self):
        self.HOST = '127.0.0.1'  # The server's hostname or IP address
        self.PORT = 65432  # The port used by the server
        self.ADDR = (self.HOST, self.PORT)

    def check_user_pass(self, username, password):
        return self.request(1,";".join([username,password]))

    def add_user(self, username, password):
        return self.request(2, ";".join([username,password]))

    def request(self, req_type, content):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.ADDR)
            s.sendall(bytes(str(req_type)+"|"+content, encoding='utf-8'))
            response = s.recv(1024).decode("utf-8")
            return int(response)


