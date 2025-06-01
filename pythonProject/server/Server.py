import socket
import json
import traceback
from typing import Optional, Callable, Dict, List
from datetime import datetime, timedelta


class Server:
    def __init__(self, port: int, logger=None):
        """
        Inicjalizuje serwer na wskazanym porcie.

        :param port: Port do nasłuchiwania
        :param logger: Opcjonalny obiekt loggera
        """
        self.port = port
        self.logger = logger

        self.on_new_reading: Optional[Callable[[dict], None]] = None
        self.on_status_change: Optional[Callable[[str], None]] = None

        self._readings: Dict[str, List[dict]] = {}
        self._running = False

    def start(self) -> None:
        """Uruchamia serwer i nasłuchuje na porcie TCP."""
        self._running = True
        self._set_status("Nasłuchiwanie")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(('', self.port))
                server_socket.listen(5)
                print(f"[SERVER] Listening on port {self.port}")

                while self._running:
                    client_socket, addr = server_socket.accept()
                    with client_socket:
                        self._handle_client(client_socket)

        except Exception as e:
            self._set_status("Błąd")
            print(f"[SERVER ERROR] {e}")
            traceback.print_exc()

        finally:
            self._set_status("Zatrzymano")

    def stop(self) -> None:
        """Zatrzymuje serwer."""
        self._running = False
        self._set_status("Zatrzymano")

    def _handle_client(self, client_socket) -> None:
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

            # Logowanie
            if self.logger:
                self.logger.log_reading(
                    sensor_id=json_data.get("sensor_id", "unknown"),
                    timestamp=datetime.now(),
                    value=json_data.get("value", 0),
                    unit=json_data.get("unit", "")
                )

            # Buforowanie i przekazanie do GUI
            self._buffer_reading(json_data)
            if self.on_new_reading:
                self.on_new_reading(json_data)

            # Wysłanie ACK
            client_socket.sendall(b"ACK\n")
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

    def _set_status(self, status: str):
        if self.on_status_change:
            self.on_status_change(status)

    def _buffer_reading(self, reading: dict):
        sensor_id = reading.get("sensor_id")
        if not sensor_id:
            return

        timestamp = datetime.fromisoformat(reading.get("timestamp"))
        value = reading.get("value", 0)

        if sensor_id not in self._readings:
            self._readings[sensor_id] = []

        self._readings[sensor_id].append({
            "timestamp": timestamp,
            "value": value,
            "unit": reading.get("unit", "")
        })

        # Zachowaj tylko ostatnie 12h
        cutoff = datetime.now() - timedelta(hours=12)
        self._readings[sensor_id] = [
            r for r in self._readings[sensor_id] if r["timestamp"] > cutoff
        ]

    def get_sensor_stats(self) -> List[dict]:
        """Zwraca statystyki do GUI: ostatnia wartość, średnie 1h i 12h dla każdego czujnika."""
        result = []
        now = datetime.now()

        for sensor_id, readings in self._readings.items():
            readings_1h = [r for r in readings if r["timestamp"] > now - timedelta(hours=1)]
            readings_12h = readings  # już przefiltrowane do 12h w _buffer_reading

            last = readings[-1] if readings else None

            if last:
                avg_1h = sum(r["value"] for r in readings_1h) / len(readings_1h) if readings_1h else 0
                avg_12h = sum(r["value"] for r in readings_12h) / len(readings_12h) if readings_12h else 0

                result.append({
                    "sensor": sensor_id,
                    "last_value": last["value"],
                    "unit": last["unit"],
                    "timestamp": last["timestamp"].isoformat(),
                    "avg_1h": round(avg_1h, 2),
                    "avg_12h": round(avg_12h, 2)
                })

        return result
