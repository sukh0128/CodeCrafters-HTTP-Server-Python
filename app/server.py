import socket
import threading

BASE = "HTTP/1.1"
OK_200 = "200 OK"
NOTFOUND_404 = "404 Not Found"
CONTENT_TYPE = "Content-Type: text/plain"
CONTENT_LENGTH = "Content-Length: "

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
        data = client_socket.recv(1024).decode().split("\r\n")
        response = BASE
        endpoint = data[0].split(" ")[1]
        if endpoint.startswith("/echo/"):
            body = data[0].split(" ")[1].split("/")[2]
            response += f" {OK_200}\r\n{CONTENT_TYPE}\r\n{CONTENT_LENGTH}{len(body)}\r\n\r\n{body}"
        elif endpoint == "/":
            response += f" {OK_200}\r\n\r\n"
        elif endpoint == "/user-agent":
            body = data[2].split(" ")[1]
            response += f" {OK_200}\r\n{CONTENT_TYPE}\r\n{CONTENT_LENGTH}{len(body)}\r\n\r\n{body}"
        else:
            response += f" {NOTFOUND_404}\r\n\r\n"
        client_socket.sendall(response.encode())
        client_socket.close()
        