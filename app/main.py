import os
MODE = os.getenv("MODE", "debug")
if MODE == "debug":
    from app.server import TCPServer
else:
    from server import TCPServer

def main():
    tcp = TCPServer("localhost", 4221)
    tcp.start_server()

if __name__ == "__main__":
    main()