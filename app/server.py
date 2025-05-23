from base64 import decode, encode
import socket
import threading
import sys
import gzip
import json

# Constants for configuration keys
CONNECTION_CLOSE_KEY = "CONNECTION_CLOSE"
BASE_KEY = "BASE"
OK_200_KEY = "OK_200"
CONTENT_ENCODING_KEY = "CONTENT_ENCODING"
ENCODING_SCHEME_KEY = "ENCODING_SCHEME"
CONTENT_TYPE_TEXT_KEY = "CONTENT_TYPE_TEXT"
CONTENT_LENGTH_KEY = "CONTENT_LENGTH"
CONTENT_TYPE_OCTET_KEY = "CONTENT_TYPE_OCTET"
CREATED_201_KEY = "CREATED_201"
NOTFOUND_404_KEY = "NOTFOUND_404"

# Load configuration
def load_config(file_path: str) -> dict:
    with open(file_path) as f:
        return json.load(f)

CONFIG = load_config("config.json")

class TCPServer:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server_socket = socket.create_server((self.host, self.port), reuse_port=True)

    def start_server(self) -> None:
        while True:
            conn, _ = self.server_socket.accept()
            threading.Thread(target=self.handle_request, args=(conn,)).start()

    def handle_request(self, client_socket: socket.socket) -> None:
        while True:
            data = client_socket.recv(1024).decode().split("\r\n")
            if not data:
                continue
            connection_close = CONFIG[CONNECTION_CLOSE_KEY] in data
            http_method, endpoint = self.parse_request(data)
            body, response = None, None
            if endpoint.startswith("/echo/"):
                response, body = self.handle_echo(endpoint, data)
            elif endpoint.startswith("/files/"):
                response, body = self.handle_files(http_method, data)
            elif endpoint == "/user-agent":
                response, body = self.handle_user_agent(data)
            elif endpoint == "/":
                response = CONFIG[BASE_KEY] + f" {CONFIG[OK_200_KEY]}"
            else:
                response = CONFIG[BASE_KEY] + f" {CONFIG[NOTFOUND_404_KEY]}\r\n\r\n"

            self.send_response(client_socket, response, body, connection_close)

    def parse_request(self, data: list) -> tuple:
        request_line = next((line for line in data if line.endswith("HTTP/1.1")), "").split(" ")
        http_method = request_line[0]
        endpoint = next((x for x in request_line if x.startswith("/")), "")
        return http_method, endpoint

    def handle_echo(self, endpoint: str, data: list) -> tuple:
        body = endpoint.split("/")[2]
        encodings = next((x.split(" ", 1)[1] for x in data if x.startswith("Accept-Encoding: ")), None)
        response = CONFIG[BASE_KEY]
        if encodings and CONFIG[ENCODING_SCHEME_KEY] in encodings:
            body = gzip.compress(body.encode('utf-8'))
            response += f" {CONFIG[OK_200_KEY]}\r\n{CONFIG[CONTENT_ENCODING_KEY]}{CONFIG[ENCODING_SCHEME_KEY]}\r\n{CONFIG[CONTENT_TYPE_TEXT_KEY]}\r\n{CONFIG[CONTENT_LENGTH_KEY]}{len(body)}"
        else:
            response += f" {CONFIG[OK_200_KEY]}\r\n{CONFIG[CONTENT_TYPE_TEXT_KEY]}\r\n{CONFIG[CONTENT_LENGTH_KEY]}{len(body)}"
        return response, body

    def handle_files(self, http_method: str, data: list) -> tuple:
        file_name = data[0].split(" ")[1].split("/")[2]
        file_directory = f"/{sys.argv[2]}"
        response = CONFIG[BASE_KEY]
        body = None
        try:
            if http_method == "GET":
                with open(f"{file_directory}/{file_name}", "r") as file:
                    content = file.read()
                    size = len(content)
                    response += f" {CONFIG[OK_200_KEY]}\r\n{CONFIG[CONTENT_TYPE_OCTET_KEY]}\r\n{CONFIG[CONTENT_LENGTH_KEY]}{size}"
                    body = content.encode('utf-8')
            elif http_method == "POST":
                body = data[5]
                with open(f"{file_directory}/{file_name}", "w") as file:
                    file.write(body)
                    response += f" {CONFIG[CREATED_201_KEY]}\r\n\r\n"
        except FileNotFoundError:
            response += f" {CONFIG[NOTFOUND_404_KEY]}\r\n\r\n"
        return response, body

    def handle_user_agent(self, data: list) -> tuple:
        body = next((x.split(" ")[1] for x in data if x.startswith("User-Agent:")), None)
        response = CONFIG[BASE_KEY]
        response += f" {CONFIG[OK_200_KEY]}\r\n{CONFIG[CONTENT_TYPE_TEXT_KEY]}\r\n{CONFIG[CONTENT_LENGTH_KEY]}{len(body)}"
        return response, body.encode('utf-8')

    def send_response(self, client_socket: socket.socket, response: str, body: bytes, connection_close: bool) -> None:
        if connection_close:
            response += f"\r\n{CONFIG[CONNECTION_CLOSE_KEY]}"
        response += "\r\n\r\n"
        try:
            if body:
                if isinstance(body, str):
                    body = body.encode("utf-8")
                client_socket.sendall(response.encode("utf-8") + body)
            else:
                client_socket.sendall(response.encode("utf-8"))
        except BrokenPipeError:
            print("[WARNING] Client disconnected before response was sent.")
        finally:
            if connection_close:
                client_socket.close()
            