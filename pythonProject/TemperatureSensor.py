import random
import math
from Sensor import Sensor
from datetime import datetime

class TemperatureSensor(Sensor):
    def __init__(self, sensor_id, name, unit="°C", min_value=-40, max_value=50, frequency=1):
        super().__init__(sensor_id, name, unit, min_value, max_value, frequency)
        self.unit = unit

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        # Uzyskaj aktualny czas
        current_hour = datetime.now().hour
        day_of_year = datetime.now().timetuple().tm_yday

        # Logika zmienności temperatury
        daily_variation = 10 * math.sin(math.pi * current_hour / 12)
        seasonal_variation = 10 * math.sin(2 * math.pi * day_of_year / 365)

        base_temperature = 15 + seasonal_variation
        value = base_temperature + daily_variation

        # Wprowadzenie zmienności w zależności od warunków pogodowych
        weather_condition = random.uniform(0.8, 1.2)
        value *= weather_condition

        # Ostateczna wartość odczytu, ograniczona do min i max
        self.last_value = max(self.min_value, min(self.max_value, value))

        # Wywołanie callbacków, jeśli są zarejestrowane
        for callback in self._callbacks:
            callback(
                sensor_id=self.sensor_id,
                timestamp=datetime.now(),  # Aktualny timestamp
                value=self.last_value,
                unit=self.unit
            )

        return self.last_value
