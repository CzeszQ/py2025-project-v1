import socket
import json
import time
from typing import Optional


class Client:
    def __init__(self, host: str, port: int, timeout: float = 5.0, retries: int = 3, logger=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.retries = retries
        self.logger = logger
        self.sock: Optional[socket.socket] = None

    def connect(self) -> None:
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
            if self.logger:
                self.logger.log_info(f"Połączono z serwerem {self.host}:{self.port}")
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Błąd połączenia z serwerem: {e}")
            raise

    def send(self, data: dict) -> bool:
        message = self._serialize(data)

        for attempt in range(1, self.retries + 1):
            try:
                if not self.sock:
                    self.connect()

                self.sock.sendall(message + b'\n')
                if self.logger:
                    self.logger.log_info(f"Wysłano dane: {data}")

                ack = self.sock.recv(1024).decode('utf-8').strip()
                if ack == 'ACK':
                    if self.logger:
                        self.logger.log_info("Otrzymano potwierdzenie ACK")
                    return True
                else:
                    if self.logger:
                        self.logger.log_error(f"Nieprawidłowe potwierdzenie: {ack}")
            except Exception as e:
                if self.logger:
                    self.logger.log_error(f"Błąd wysyłania danych (próba {attempt}): {e}")
                time.sleep(1)

        return False

    def close(self) -> None:
        if self.sock:
            try:
                self.sock.close()
                if self.logger:
                    self.logger.log_info("Zamknięto połączenie z serwerem")
            except Exception as e:
                if self.logger:
                    self.logger.log_error(f"Błąd przy zamykaniu połączenia: {e}")
        self.sock = None

    def _serialize(self, data: dict) -> bytes:
        return json.dumps(data).encode('utf-8')

    def _deserialize(self, raw: bytes) -> dict:
        return json.loads(raw.decode('utf-8'))
