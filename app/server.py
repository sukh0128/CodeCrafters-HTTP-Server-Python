from base64 import decode, encode
import socket
import threading
import sys
import gzip

BASE = "HTTP/1.1"
OK_200 = "200 OK"
CREATED_201 = "201 Created"
NOTFOUND_404 = "404 Not Found"
CONTENT_TYPE_TEXT = "Content-Type: text/plain"
CONTENT_TYPE_OCTET = "Content-Type: application/octet-stream"
CONTENT_LENGTH = "Content-Length: "
CONTENT_ENCODING = "Content-Encoding: "
ENCODING_SCHEME = "gzip"
CONNECTION_CLOSE = "Connection: close"
class TCPServer:
    def __init__(self, host:str, port:int) -> None:
        self.host = host
        self.port = port
        self.server_socket = socket.create_server((self.host, self.port), reuse_port=True)
    
    def start_server(self) -> None:
        while True:
            conn, addr = self.server_socket.accept()   
            threading.Thread(target=self.handle_request, args=(conn,)).start()

    def handle_request(self, client_socket: socket.socket) -> None: 
        while True:
            data = client_socket.recv(1024).decode().split("\r\n")
            if not data:
                break
            connection_close = True if "Connection: close" in data else False
            response = BASE
            request = data[0].split(" ")
            http_method = request[0]
            endpoint = next((x for x in request if x.startswith("/")), "")
            body = None
            if endpoint.startswith("/echo/"):
                body = endpoint.split("/")[2]
                encodings = next((x.split(" ", 1)[1] for x in data if x.startswith("Accept-Encoding: ")), None)
                    
                if encodings and ENCODING_SCHEME in encodings:
                    body = gzip.compress(body.encode('utf-8'))
                    response += f" {OK_200}\r\n{CONTENT_ENCODING}{ENCODING_SCHEME}\r\n{CONTENT_TYPE_TEXT}\r\n{CONTENT_LENGTH}{len(body)}"
                else:
                    response += f" {OK_200}\r\n{CONTENT_TYPE_TEXT}\r\n{CONTENT_LENGTH}{len(body)}"
                if connection_close:
                    response+= f"\r\n{CONNECTION_CLOSE}"
                response+="\r\n\r\n"
            elif endpoint.startswith("/files/"):
                fileName = data[0].split(" ")[1].split("/")[2]
                file_directory = f"/{sys.argv[2]}"
                try:
                    if http_method == "GET":
                        with open(f"{file_directory}/{fileName}", "r" ) as file:
                            content = file.read()
                            size = len(content)
                            response += f" {OK_200}\r\n{CONTENT_TYPE_OCTET}\r\n{CONTENT_LENGTH}{size}"
                            if connection_close:
                                response+= f"\r\n{CONNECTION_CLOSE}"
                            
                            response += f"\r\n\r\n{content}"
                    elif http_method == "POST":
                        body = data[5]
                        with open(f"{file_directory}/{fileName}", "w") as file:
                            file.write(body)
                            response += f" {CREATED_201}\r\n\r\n"
                except FileNotFoundError:
                    response += f" {NOTFOUND_404}\r\n\r\n"
                else:
                    file.close()
            elif endpoint == "/":
                response += f" {OK_200}"
                if connection_close:
                    response+= f"\r\n{CONNECTION_CLOSE}"
                response+="\r\n\r\n"
            elif endpoint == "/user-agent":
                body = next((x.split(" ")[1] for x in data if x.startswith("User-Agent:")), None)
                response += f" {OK_200}\r\n{CONTENT_TYPE_TEXT}\r\n{CONTENT_LENGTH}{len(body)}"
                if connection_close:
                    response+= f"\r\n{CONNECTION_CLOSE}"
                response+="\r\n\r\n"
            else:
                response += f" {NOTFOUND_404}\r\n\r\n"
            body = body.encode("utf-8") if type(body) == str else body
            if body:
                client_socket.sendall(response.encode("utf-8")+body)
            else:
                client_socket.sendall(response.encode("utf-8"))
            if connection_close:
                client_socket.close()
            