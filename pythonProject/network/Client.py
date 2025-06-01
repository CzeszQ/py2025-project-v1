import socket
import json
import time
from typing import Optional


class Client:
    def __init__(self, host: str, port: int, timeout: float = 5.0, retries: int = 3, logger=None):
        """
        Inicjalizuje klienta sieciowego do przesyłania danych do serwera TCP.

        :param host: Adres IP lub nazwa hosta serwera
        :param port: Port TCP serwera
        :param timeout: Maksymalny czas oczekiwania na połączenie (w sekundach)
        :param retries: Liczba prób ponowienia połączenia przy błędzie
        :param logger: Obiekt loggera do logowania zdarzeń (opcjonalny)
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.retries = retries
        self.logger = logger

    def connect(self) -> None:
        """
        Metoda zachowana dla zgodności ze specyfikacją – połączenie tworzone jest przy każdym send().
        """
        pass

    def send(self, data: dict) -> bool:
        """
        Wysyła dane do serwera w formacie JSON, czeka na potwierdzenie ACK.

        :param data: Słownik danych do wysłania
        :return: True jeśli wysłano i odebrano ACK, False w przeciwnym razie
        """
        message = self._serialize(data) + b"\n"

        for attempt in range(1, self.retries + 1):
            try:
                with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
                    sock.sendall(message)
                    if self.logger:
                        self.logger.log_info(f"Wysłano dane: {data}")

                    ack = sock.recv(1024).strip()
                    if ack == b"ACK":
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
        """
        Zamyka połączenie – w tej wersji połączenie jest tymczasowe, więc nic nie robi.
        """
        if self.logger:
            self.logger.log_info("Zakończono działanie klienta.")

    def _serialize(self, data: dict) -> bytes:
        """
        Serializuje słownik do formatu JSON w postaci bajtów.

        :param data: Dane do serializacji
        :return: Zserializowane dane w formacie JSON jako bajty
        """
        return json.dumps(data).encode('utf-8')

    def _deserialize(self, raw: bytes) -> dict:
        """
        Deserializuje dane JSON w formacie bajtowym do słownika.

        :param raw: Surowe bajty zawierające JSON
        :return: Słownik z danymi
        """
        return json.loads(raw.decode('utf-8'))
