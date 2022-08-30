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

        if path == "/messages":
            path = "messages.json"

        if path.startswith("/") and path != "/":
            path = '.' + path

        traversal_attack = True if ".." in path else False
        excluded_filetypes = ('.py') #Tuple, accepts multiple filetypes
        forbidden_recourse = path.endswith(excluded_filetypes)
        file_exists = exists(path)

        if traversal_attack or forbidden_recourse:
            self.respond_status(HTTPStatus.FORBIDDEN)

        elif not file_exists and method != "POST":
            self.respond_status(HTTPStatus.NOT_FOUND)
        

        elif path == "messages.json":
            file = "messages.json"
            if method == "GET":
                self.messages_handle_get(file)
            elif method == "POST":
                self.messages_handle_post(file)
            elif method == "PUT":
                self.messages_handle_put(file)
            elif method == "DELETE":
                self.messages_handle_delete(file)
            else:
                self.bad_request()

        else:
            if method == "GET":
                self.handle_get(path)
            elif method == "POST":
                self.handle_post(path)
            else:
                self.bad_request()

    def handle_get(self, path):
        body = self.get_data_from_path(path)
        self.respond_with_body(HTTPStatus.OK, body)

    def get_body(self):
        data = None
        content_len = 0
        while data != '':
            data = self.rfile.readline().strip().decode()
            if data.startswith("Content-Length"):
                content_len = int(data.split()[-1])
        return self.rfile.readline(content_len).decode('utf-8')

    def handle_post(self, path):
        valid_paths = ("test.txt", "./test.txt")
        if path not in valid_paths:
            return self.respond_status(HTTPStatus.FORBIDDEN)
        
        # post_data = bytes(self.get_body(),encoding="utf-8")
        post_data = self.get_body()
        f = open(path, "a+")
        f.write(post_data)
        f.close()

        response_body = self.get_data_from_path(path)
        self.respond_with_body(HTTPStatus.CREATED, response_body)

    def respond_with_body(self, status, body):
        content_length = f"Content-Length: {len(body)}\n"
        headers = f"{self.protocol}{status}\n{self.content_type}{content_length}{self.connection}"
        self.wfile.write(bytes(headers, encoding="utf-8"))
        self.wfile.write(b"\n")
        self.wfile.write(body)

    def respond_status(self, status_code):
        response = f"{self.protocol}{status_code}"
        self.wfile.write(bytes(response, encoding="utf-8"))

    def get_data_from_path(self, path):
        if path == "/":
            path = "index.html"
        
        f = open(path, "rb")
        data = f.read()
        f.close()
        return data

    
    def messages_handle_get(self, path):
        body = self.get_data_from_path(path)
        self.respond_with_body(HTTPStatus.OK, body)

    def messages_handle_post(self, path):
        post_data = bytes(self.get_body(),encoding="utf-8")

        try:
            post_data_json = json.loads(post_data)
        except:
            return self.bad_request()

        if post_data_json.get("text") == None:
            return self.bad_request()

        with open(path, 'r') as f:
            messages = json.load(f)
            last_id = messages[-1]["id"]
        
        data_with_id = {}
        data_with_id["id"] = last_id + 1
        data_with_id["text"] = post_data_json["text"]

        with open(path,'w') as f:
            messages.append(data_with_id)
            json.dump(messages, f, indent = 4)
        
        self.respond_with_body(HTTPStatus.CREATED, post_data)
    
    def messages_handle_put(self, path):
        put_data = self.get_body()

        try:
            put_data_json = json.loads(put_data)
        except:
            return self.bad_request()

        if put_data_json.get("text") == None or put_data_json.get("id") == None:
            return self.bad_request()

        message_id = put_data_json["id"]
        with open(path,'r') as f:
            messages = json.load(f)

        edited = False
        for idx, message in enumerate(messages):
            if message["id"] == message_id:
                messages[idx] = put_data_json
                edited = True 

        if not edited:
            return self.respond_status(HTTPStatus.NOT_FOUND)

        with open(path, "w") as file:
            json.dump(messages, file, indent = 4)

        self.respond_status(HTTPStatus.OK if edited == True else HTTPStatus.CREATED)


    def messages_handle_delete(self, path):
        delete_data = self.get_body()

        try:
            delete_data_json = json.loads(delete_data)
        except:
            return self.bad_request()

        if delete_data_json.get("id") == None:
            return self.bad_request()
        message_id = delete_data_json["id"]

        with open(path) as data_file:
            messages = json.load(data_file)

        deleted = False    

        for message in messages:
            if message["id"] == message_id:
                messages.remove(message)
                deleted = True

        with open(path, "w") as file:
            json.dump(messages, file, indent = 4)

        self.respond_status(HTTPStatus.NO_CONTENT if deleted else HTTPStatus.NOT_FOUND)
    
    def bad_request(self):
        self.respond_status(HTTPStatus.BAD_REQUEST)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        print("Serving at: http://{}:{}".format(HOST, PORT))
        server.serve_forever()
