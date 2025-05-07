import math
from datetime import datetime
import random  # Importujemy cały moduł random
from Sensor import Sensor

class PressureSensor(Sensor):
    def __init__(self, sensor_id, name, unit="hPa", min_value=950, max_value=1050, frequency=1):
        super().__init__(sensor_id, name, unit, min_value, max_value, frequency)
        self.unit = unit

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        now = datetime.now()
        hour = now.hour
        day_of_year = now.timetuple().tm_yday

        daily_variation = 2 * math.sin(math.pi * hour / 12)
        seasonal_variation = 5 * math.sin(2 * math.pi * day_of_year / 365)
        weather_effect = random.uniform(-3, 3)  # Teraz działa poprawnie

        base_pressure = 1013 + seasonal_variation + daily_variation + weather_effect
        self.last_value = max(self.min_value, min(self.max_value, base_pressure))

        # Logowanie przez callbacki
        for callback in self._callbacks:
            callback(
                sensor_id=self.sensor_id,
                timestamp=now,
                value=self.last_value,
                unit=self.unit
            )

        return self.last_value
