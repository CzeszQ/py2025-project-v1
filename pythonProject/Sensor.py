
import random
import time

class Sensor:
    def __init__(self, sensor_id, name, unit, min_value, max_value, frequency=1):
        self.sensor_id = sensor_id
        self.name = name
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.frequency = frequency  # Częstotliwość odczytów w sekundach
        self.active = True
        self.last_value = None
        self.last_read_time = time.time()  # Czas ostatniego odczytu

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        # Sprawdzenie, czy minęła odpowiednia ilość czasu od ostatniego odczytu
        current_time = time.time()
        if current_time - self.last_read_time < self.frequency:
            return self.last_value  # Zwróć ostatnią wartość, jeśli jeszcze nie minął czas

        value = random.uniform(self.min_value, self.max_value)
        self.last_value = value
        self.last_read_time = current_time  # Aktualizujemy czas ostatniego odczytu
        return value

    def calibrate(self, calibration_factor):
        """
        Kalibruje ostatni odczyt przez przemnożenie go przez calibration_factor.
        Jeśli nie wykonano jeszcze odczytu, wykonuje go najpierw.
        """
        if self.last_value is None:
            self.read_value()

        self.last_value *= calibration_factor
        return self.last_value

    def get_last_value(self):
        """
        Zwraca ostatnią wygenerowaną wartość, jeśli była wygenerowana.
        """
        if self.last_value is None:
            return self.read_value()
        return self.last_value

    def start(self):
        """
        Włącza czujnik.
        """
        self.active = True

    def stop(self):
        """
        Wyłącza czujnik.
        """
        self.active = False

    def __str__(self):
        return f"Sensor(id={self.sensor_id}, name={self.name}, unit={self.unit})"