import random
import math
from datetime import datetime
from Sensor import Sensor
from TemperatureSensor import TemperatureSensor


class HumiditySensor(Sensor):
    def __init__(self, sensor_id, name, min_value=0, max_value=100, frequency=1):
        """
        Inicjalizacja czujnika wilgotności.
        Uwzględnia zmienność wilgotności w zależności od temperatury i pory dnia.
        """
        super().__init__(sensor_id, name, "%", min_value, max_value, frequency)

    def read_value(self):
        """
        Generuje realistyczny odczyt wilgotności, uwzględniając temperaturę oraz zmienność w ciągu dnia.
        """
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        # Zmienność wilgotności na podstawie temperatury
        temp = TemperatureSensor("temp_01", "Temperature", -20,
                                 50).read_value()  # Można połączyć z czujnikiem temperatury
        base_humidity = 50 + (temp - 20) * 2  # Wilgotność wzrasta z temperaturą (można zmienić ten wzór)

        # Zmienność wilgotności w ciągu dnia (wysoka wilgotność rano i wieczorem)
        daily_variation = 30 * math.sin(math.pi * datetime.now().hour / 12)

        value = base_humidity + daily_variation
        self.last_value = max(self.min_value, min(self.max_value, value))  # Ograniczamy do zakresu
        return self.last_value