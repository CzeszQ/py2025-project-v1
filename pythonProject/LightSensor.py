import math
import numpy as np
from datetime import datetime
from random import choices, gauss
from Sensor import Sensor


class LightSensor(Sensor):
    def __init__(self, sensor_id, name, unit="lux", min_value=0, max_value=25000, frequency=1):
        super().__init__(sensor_id, name, unit, min_value, max_value, frequency)
        self.unit = unit
        self.noise_level = 0.05
        self.baseline_indoor = 50

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        hour = datetime.now().hour
        minute = datetime.now().minute

        time_decimal = hour + minute / 60.0
        base_light = self._calculate_natural_light_cycle(time_decimal)

        # Warunki pogodowe
        condition = choices(
            ['sunny', 'cloudy', 'overcast', 'rainy', 'stormy'],
            weights=[0.3, 0.25, 0.2, 0.15, 0.1]
        )[0]

        condition_factor = {
            'sunny': 1.0,
            'cloudy': 0.7,
            'overcast': 0.4,
            'rainy': 0.25,
            'stormy': 0.15
        }

        # Obliczenie podstawowej wartości
        light_level = base_light * condition_factor[condition]

        # Dodanie realistycznego szumu
        light_level = self._add_realistic_noise(light_level)

        # Zapewnienie minimalnego poziomu oświetlenia i ograniczenie do zakresu
        light_level = max(self.baseline_indoor, light_level)
        self.last_value = max(self.min_value, min(self.max_value, light_level))
        self.last_condition = condition

        # Logowanie przez callbacki
        for callback in self._callbacks:
            callback(
                sensor_id=self.sensor_id,
                timestamp=datetime.now(),
                value=self.last_value,
                unit=self.unit
            )

        return self.last_value

    def _calculate_natural_light_cycle(self, time_decimal):
        """
        Oblicza naturalny cykl światła dziennego z realistycznymi wartościami LUX
        """
        # Przesunięcie fazowe tak, aby maksimum było o 12:00
        phase_shift = -6  # godziny
        adjusted_time = time_decimal + phase_shift

        # Użycie cosinusa dla płynnego przejścia (zawsze >= 0)
        cycle_factor = (math.cos(2 * math.pi * adjusted_time / 24) + 1) / 2

        # Realistyczne wartości dla różnych pór dnia
        max_daylight = 20000  # Jasny dzień słoneczny
        min_nightlight = 0.1  # Ciemność nocna

        return min_nightlight + (max_daylight - min_nightlight) * cycle_factor

    def _add_realistic_noise(self, base_value):
        """
        Dodaje realistyczny szum do odczytu czujnika
        """
        # Szum gaussowski proporcjonalny do wartości sygnału
        noise_std = base_value * self.noise_level
        noise = gauss(0, noise_std)

        # Dodatkowy szum kwantyzacji (typowy dla czujników cyfrowych)
        quantization_noise = gauss(0, 1.0)

        # Szum flicker charakterystyczny dla oświetlenia AC
        flicker_noise = gauss(0, base_value * 0.01) if base_value > 100 else 0

        return base_value + noise + quantization_noise + flicker_noise