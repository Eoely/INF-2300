#!/usr/bin/env python3
import socketserver
from os.path import exists
from http import HTTPStatus


"""
Written by: Raymon Skjørten Hansen
Email: raymon.s.hansen@uit.no
Course: INF-2300 - Networking
UiT - The Arctic University of Norway
May 9th, 2019
"""

class MyTCPHandler(socketserver.StreamRequestHandler):
    """
    This class is responsible for handling a request. The whole class is
    handed over as a parameter to the server instance so that it is capable
    of processing request. The server will use the handle-method to do this.
    It is instantiated once for each request!
    Since it inherits from the StreamRequestHandler class, it has two very
    usefull attributes you can use:

    rfile - This is the whole content of the request, displayed as a python
    file-like object. This means we can do readline(), readlines() on it!

    wfile - This is a file-like object which represents the response. We can
    write to it with write(). When we do wfile.close(), the response is
    automatically sent.

    The class has three important methods:
    handle() - is called to handle each request.
    setup() - Does nothing by default, but can be used to do any initial
    tasks before handling a request. Is automatically called before handle().
    finish() - Does nothing by default, but is called after handle() to do any
    necessary clean up after a request is handled.
    """
    def handle(self):
        """
        This method is responsible for handling an http-request. You can, and should(!),
        make additional methods to organize the flow with which a request is handled by
        this method. But it all starts here!
        """

        self.protocol = "HTTP/1.1 "
        self.status = f"{HTTPStatus.NOT_IMPLEMENTED}\n"
        
        data = self.rfile.readline().strip()
        method = data.split()[0].decode()
        path = data.split()[1].decode()
        print("method", method)
        print('path', path)

        if method == "GET":
            self.handle_get(path)
        elif method == "POST":
            self.handle_post(path)
        else:
            self.not_implemented()


    def handle_get(self, path: str):
        file_exists = exists(path)
        traversal_attack = path.startswith("..")
        excluded_filetypes = ('.py') #Tuple, accepts multiple filetypes
        forbidden_recourse = path.endswith(excluded_filetypes)

        if traversal_attack or forbidden_recourse:
            self.status = f"{HTTPStatus.FORBIDDEN}\n"
            response = f"{self.protocol}{self.status}"
            self.wfile.write(bytes(response, encoding="utf-8"))

        elif file_exists:
            self.status = f"{HTTPStatus.OK}\n"
            body = self.load_index()
            content_type = "Content-Type: text/html; charset=utf-8\n"
            content_length = f"Content-Length: {len(body)}\n"
            connection = "Connection: close\n"

            headers = f"{self.protocol}{self.status}{content_type}{content_length}{connection}"
            self.wfile.write(bytes(headers, encoding="utf-8"))
            self.wfile.write(b"\n")
            self.wfile.write(body)

        elif not file_exists:
            self.status = f"{HTTPStatus.NOT_FOUND}\n"
            response = f"{self.protocol}{self.status}"
            self.wfile.write(bytes(response, encoding="utf-8"))

        else:
            self.not_implemented()
    
    def handle_post(self, path: str):
        self.not_implemented()

    def load_index(self):
        f = open("index.html", "rb")
        data = f.read()
        f.close()
        return data

    def not_implemented(self):
        self.print_data()
        self.status = f"{HTTPStatus.NOT_IMPLEMENTED}\n"
        response = f"{self.protocol}{self.status}"
        self.wfile.write(bytes(response, encoding="utf-8"))

    def print_data(self):
        print('printing data')
        while True:
            data = self.rfile.readline().strip().decode()
            print('data =', data)
            if data == '':
                return   

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        print("Serving at: http://{}:{}".format(HOST, PORT))
        server.serve_forever()
