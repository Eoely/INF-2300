#!/usr/bin/env python3
import socketserver
import json
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
        self.content_type = "Content-Type: text/html; charset=utf-8\n"
        self.connection = "Connection: close\n"

        data = self.rfile.readline().strip()
        method = data.split()[0].decode()
        path = data.split()[1].decode()

        if path.startswith('/') and path != "/":
            path = '.' + path

        if path == "./messages":
            if method == "GET":
                self.messages_handle_get()
            elif method == "POST":
                self.messages_handle_post()
            elif method == "PUT":
                self.messages_handle_put()
            else:
                self.not_implemented()

        else:
            if method == "GET":
                self.handle_get(path)
            elif method == "POST":
                self.handle_post(path)
            else:
                self.not_implemented()

    def handle_get(self, path: str):
        traversal_attack = path.startswith("..")
        excluded_filetypes = ('.py') #Tuple, accepts multiple filetypes
        forbidden_recourse = path.endswith(excluded_filetypes)
        file_exists = exists(path)

        if traversal_attack or forbidden_recourse:
            self.respond_error(HTTPStatus.FORBIDDEN)

        elif not file_exists:
            self.respond_error(HTTPStatus.NOT_FOUND)

        elif file_exists:
            self.respond_ok(path)

        else:
            self.not_implemented()
    
    def handle_post(self, path):
        valid_paths = ("test.txt", "./test.txt")
        if path not in valid_paths:
            return self.respond_error(HTTPStatus.FORBIDDEN)
        
        #Get Content-Length header
        content_len = 0
        while True:
            data = self.rfile.readline().strip().decode()
            if data.startswith("Content-Length"):
                content_len = int(data.split()[-1])
                continue
            if data == '':
                break

        post_data = self.rfile.readline(content_len).decode('utf-8')
        f = open(path, "a+")
        f.write(post_data)
        f.close()

        self.respond_ok(path)

    def respond_ok(self, path):
        self.status = f"{HTTPStatus.OK}\n"
        body = self.get_data_from_path(path)
        content_length = f"Content-Length: {len(body)}\n"
        headers = f"{self.protocol}{self.status}{self.content_type}{content_length}{self.connection}"
        self.wfile.write(bytes(headers, encoding="utf-8"))
        self.wfile.write(b"\n")
        self.wfile.write(body)

    def respond_error(self, status_code):
        response = f"{self.protocol}{status_code}"
        self.wfile.write(bytes(response, encoding="utf-8"))

    def get_data_from_path(self, path: str):
        if path == "/":
            path = "index.html"
        
        f = open(path, "rb")
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
    
    def messages_handle_get(self):
        path = "messages.json"
        self.respond_ok(path)

    def messages_handle_post(self):
        path = "messages.json"
        #Get Content-Length header
        content_len = 0
        while True:
            data = self.rfile.readline().strip().decode()
            if data.startswith("Content-Length"):
                content_len = int(data.split()[-1])
                continue
            if data == '':
                break
        post_data = self.rfile.readline(content_len).decode('utf-8')

        #TODO: validate json format, need to be sent from postman. Data from web form is encoded with %20 and all that
        with open(path,'r') as f:
            # print('content length from server',len(path))
            data = json.load(f)
            data.append(json.loads(post_data))

        with open(path, "w") as file:
            json.dump(data, file, indent = 4)
        
        self.respond_ok(path)
    
    def messages_handle_put(self):
        path = "messages.json"
        #Get Content-Length header
        content_len = 0
        while True:
            data = self.rfile.readline().strip().decode()
            if data.startswith("Content-Length"):
                content_len = int(data.split()[-1])
                continue
            if data == '':
                break
        put_data = self.rfile.readline(content_len).decode('utf-8')
        put_data_json = json.loads(put_data)
        message_id = put_data_json["id"]

        #TODO: validate json format, need to be sent from postman. Data from web form is encoded with %20 and all that
        with open(path,'r') as f:
            messages = json.load(f)
            
        for idx, obj in enumerate(messages):
            if messages[idx]["id"] == message_id:
                messages[idx] = put_data_json

        with open(path, "w") as file:
            json.dump(messages, file, indent = 4)
        
        self.respond_ok(path)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        print("Serving at: http://{}:{}".format(HOST, PORT))
        server.serve_forever()
