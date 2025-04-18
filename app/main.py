import socket  # noqa: F401


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, addr = server_socket.accept()    
    data = conn.recv(1024).decode().split(" ")
    if data[1].startswith("/echo/"):
        body = data[1].split("/")[2]
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n{body}"
        conn.sendall(response.encode())
    else:
        conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
        
if __name__ == "__main__":
    main()
