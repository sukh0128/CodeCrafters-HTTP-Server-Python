import socket  # noqa: F401
BASE = "HTTP/1.1"
OK_200 = "200 OK"
NOTFOUND_404 = "404 Not Found"
CONTENT_TYPE = "Content-Type: text/plain"
CONTENT_LENGTH = "Content-Length: "

def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, addr = server_socket.accept()    
    data = conn.recv(1024).decode().split(" ")
    response = BASE
    if data[1].startswith("/echo/"):
        body = data[1].split("/")[2]
        response += f" {OK_200}\r\n{CONTENT_TYPE}\r\n{CONTENT_LENGTH}{len(body)}\r\n\r\n{body}"
    elif data[1] == "/":
        response += f" {OK_200}\r\n\r\n"
    else:
        response += f" {NOTFOUND_404}\r\n\r\n"
    conn.sendall(response.encode())
        
if __name__ == "__main__":
    main()
