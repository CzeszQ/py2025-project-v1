from datetime import datetime
import math
from Sensor import Sensor
from TemperatureSensor import TemperatureSensor


class HumiditySensor(Sensor):
    def __init__(self, sensor_id, name, unit="%", min_value=0, max_value=100, frequency=1, temperature_sensor=None):
        # Wywołanie konstruktora klasy bazowej (Sensor)
        super().__init__(sensor_id, name, unit, min_value, max_value, frequency)
        self.unit = unit

        # Tworzymy czujnik temperatury, jeśli nie został przekazany
        if temperature_sensor is None:
            # Zakładając, że chcesz stworzyć nowy obiekt TemperatureSensor
            self.temperature_sensor = TemperatureSensor(sensor_id=sensor_id + "_temp", name=name + "_Temperature",
                                                        unit="°C")
        else:
            self.temperature_sensor = temperature_sensor

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        # Pobierz temperaturę z przekazanego czujnika
        temp = self.temperature_sensor.read_value()

        # Oblicz wilgotność w zależności od temperatury i pory dnia
        base_humidity = 60 - (temp - 20) * 1.5  # wilgotność spada przy wyższej temperaturze
        daily_variation = 20 * math.sin(math.pi * datetime.now().hour / 12)

        value = base_humidity + daily_variation
        self.last_value = max(self.min_value, min(self.max_value, value))

        # Logowanie przez callbacki
        for callback in self._callbacks:
            callback(
                sensor_id=self.sensor_id,
                timestamp=datetime.now(),
                value=self.last_value,
                unit=self.unit
            )

        return self.last_value
