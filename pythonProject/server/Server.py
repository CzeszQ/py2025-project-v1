import socket
import json
import traceback
from typing import Optional
from datetime import datetime

class Server:
    def __init__(self, port: int, logger=None):
        """
        Inicjalizuje serwer na wskazanym porcie.

        :param port: Port do nasłuchiwania
        :param logger: Opcjonalny obiekt loggera do logowania zdarzeń
        """
        self.port = port
        self.logger = logger

    def start(self) -> None:
        """Uruchamia nasłuchiwanie połączeń i obsługę klientów."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('', self.port))
            server_socket.listen(5)
            print(f"[SERVER] Listening on port {self.port}")

            while True:
                client_socket, addr = server_socket.accept()
                with client_socket:
                    self._handle_client(client_socket)

    def _handle_client(self, client_socket) -> None:
        """Odbiera dane, wysyła ACK i wypisuje je na konsolę."""
        try:
            data = b""
            while not data.endswith(b"\n"):
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                data += chunk

            json_data = json.loads(data.decode('utf-8'))
            print(f"[SERVER] Received data:")
            for k, v in json_data.items():
                print(f"  {k}: {v}")

            # Logowanie przez Logger, jeśli podany
            if self.logger:
                self.logger.log_reading(
                    sensor_id=json_data.get("sensor_id", "unknown"),
                    timestamp=datetime.now(),
                    value=json_data.get("value", 0),
                    unit=json_data.get("unit", "")
                )

            # Wysłanie ACK
            client_socket.sendall(b"ACK\n")
            if self.logger:
                print("[SERVER] ACK sent")
        except Exception as e:
            print(f"[SERVER ERROR] {e}")
            traceback.print_exc()

            if self.logger:
                self.logger.log_reading(
                    sensor_id="server",
                    timestamp=datetime.now(),
                    value=0,
                    unit="ERROR"
                )
