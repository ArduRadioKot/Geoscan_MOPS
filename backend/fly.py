import socket

HOST = "10.42.0.1"
PORT = 8089
from datetime import datetime
def fly_start():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.sendall(b"start")

fly_start()
