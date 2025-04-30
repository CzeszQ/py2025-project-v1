class LightSensor(Sensor):
    def __init__(self, sensor_id, name, min_value=0, max_value=10000, frequency=1):
        super().__init__(sensor_id, name, "lux", min_value, max_value, frequency)

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        hour = datetime.now().hour
        base_light = self.max_value * math.sin(math.pi * hour / 12)

        # Losowa symulacja pogody
        condition = random.choices(
            ['sunny', 'cloudy', 'rainy', 'stormy'],
            weights=[0.4, 0.3, 0.2, 0.1]
        )[0]

        # Przypisanie współczynnika redukcji światła
        condition_factor = {
            'sunny': 1.0,
            'cloudy': 0.6,
            'rainy': 0.3,
            'stormy': 0.1
        }

        light_level = base_light * condition_factor[condition]
        self.last_value = max(self.min_value, min(self.max_value, light_level))
        return self.last_value
