import random
import math
from datetime import datetime
from Sensor import Sensor

class TemperatureSensor(Sensor):
    def __init__(self, sensor_id, name, min_value=-20, max_value=50, frequency=1):
        """
        Inicjalizacja czujnika temperatury.
        Zakłada zakres od -20°C do 50°C.
        Uwzględnia zmienność temperatury w ciągu dnia oraz sezonową zmienność.
        """
        super().__init__(sensor_id, name, "°C", min_value, max_value, frequency)

    def read_value(self):
        """
        Generuje realistyczny odczyt temperatury w ciągu dnia, uwzględniając zmienność sezonową i cykle dzienne.
        """
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        # Pobieranie aktualnej godziny (24-godzinna)
        current_hour = datetime.now().hour
        day_of_year = datetime.now().timetuple().tm_yday

        # Zmienność temperatury w ciągu dnia (zakłada się, że rano i wieczorem jest chłodniej)
        daily_variation = 10 * math.sin(math.pi * current_hour / 12)  # Zmienność w ciągu dnia

        # Sezonowa zmienność (zimą chłodniej, latem cieplej)
        seasonal_variation = 10 * math.sin(2 * math.pi * day_of_year / 365)

        # Średnia temperatura w danym miejscu (np. 15°C w ciągu dnia)
        bbase_temperature = 15 + seasonal_variation
        value = base_temperature + daily_variation
        weather_condition = random.uniform(0.8, 1.2)
        # Finalna wartość
        value *= weather_condition
        self.last_value = max(self.min_value, min(self.max_value, value))
        return self.last_value