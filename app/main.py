from app.server import TCPServer
def main():
    tcp = TCPServer("localhost", 4221)
    tcp.start_server()

if __name__ == "__main__":
    main()