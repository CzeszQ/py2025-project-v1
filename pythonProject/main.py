from Logger import Logger

from TemperatureSensor import TemperatureSensor
from HumiditySensor import HumiditySensor
from LightSensor import LightSensor
from PressureSensor import PressureSensor
from datetime import datetime
import time

def main():
    # Inicjalizacja loggera z plikiem konfiguracyjnym
    logger = Logger("config.json")
    logger.start()

    # Tworzenie czujników
    temp_sensor = TemperatureSensor(sensor_id="T1", name="Temp Sensor", unit="°C")
    hum_sensor = HumiditySensor(sensor_id="H1", name="Humidity Sensor", unit="%")
    light_sensor = LightSensor(sensor_id="L1", name="Light Sensor", unit="lux")
    pressure_sensor = PressureSensor(sensor_id="P1", name="Pressure Sensor", unit="hPa")

    # Rejestracja callbacków dla każdego czujnika
    temp_sensor.register_callback(logger.log_reading)
    hum_sensor.register_callback(logger.log_reading)
    light_sensor.register_callback(logger.log_reading)
    pressure_sensor.register_callback(logger.log_reading)

    try:
        # Symulacja odczytów w pętli
        for _ in range(10):
            # Odczyty z czujników
            temp_sensor.read_value()
            hum_sensor.read_value()
            light_sensor.read_value()
            pressure_sensor.read_value()

            # Przerwa 1 sekunda
            time.sleep(1)

    finally:
        # Zakończenie logowania
        logger.stop()
        print("Logowanie zakończone.")

if __name__ == "__main__":
    main()
