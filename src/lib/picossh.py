import os
import socketpool
import board
import wifi
import select
import supervisor

class PicoSSH:
    def __init__(self, port=22):
        self.port = port
        self.pool = socketpool.SocketPool(wifi.radio)  # Use CircuitPython's network socket pool
        self.server_socket = self.pool.socket(self.pool.AF_INET, self.pool.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen(1)
        self.server_socket.setblocking(False)  # Non-blocking mode

    def start_server(self):
        print(f"Starting SSH server on port {self.port}...")
        while True:
            try:
                conn, addr = self.server_socket.accept()
                print(f"Connection from {addr}")
                conn.send(b"Welcome to Pico SSH!\n")
                conn.close()
            except OSError:
                pass  # No connection yet, keep looping

    def update(self):
        """Call this in the main loop to keep checking for new connections."""
        try:
            conn, addr = self.server_socket.accept()
            print(f"Connection from {addr}")
            conn.send(b"Welcome to Pico SSH!\n")
            conn.close()
        except OSError:
            pass  # No connection yet, keep going

