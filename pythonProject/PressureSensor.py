class PressureSensor(Sensor):
    def __init__(self, sensor_id, name, min_value=950, max_value=1050, frequency=1):
        super().__init__(sensor_id, name, "hPa", min_value, max_value, frequency)

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        now = datetime.now()
        hour = now.hour
        day_of_year = now.timetuple().tm_yday

        # Wariacje dzienne i sezonowes
        daily_variation = 2 * math.sin(math.pi * hour / 12)
        seasonal_variation = 5 * math.sin(2 * math.pi * day_of_year / 365)

        # Pogodowy wpływ (symulowany losowo)
        weather_effect = random.uniform(-3, 3)

        base_pressure = 1013 + seasonal_variation + daily_variation + weather_effect
        self.last_value = max(self.min_value, min(self.max_value, base_pressure))
        return self.last_value
