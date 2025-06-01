from Logger import Logger
from TemperatureSensor import TemperatureSensor
from HumiditySensor import HumiditySensor
from LightSensor import LightSensor
from PressureSensor import PressureSensor
from network.Client import Client

from datetime import datetime
import time

def main():
    # Inicjalizacja loggera (opcjonalnie)
    logger = Logger("config.json")
    logger.start()

    # Inicjalizacja klienta
    client = Client(host="127.0.0.1", port=9999, logger=logger)

    # Funkcja do wysyłania odczytu do serwera
    def send_to_server(sensor_id, timestamp, value, unit):
        success = client.send({
            "sensor_id": sensor_id,
            "timestamp": timestamp.isoformat(),
            "value": value,
            "unit": unit
        })
        if not success and logger:
            logger.log_error(f"Błąd wysyłania danych z czujnika {sensor_id}")

    # Tworzenie czujników
    temp_sensor = TemperatureSensor(sensor_id="T1", name="Temp Sensor", unit="°C")
    hum_sensor = HumiditySensor(sensor_id="H1", name="Humidity Sensor", unit="%")
    light_sensor = LightSensor(sensor_id="L1", name="Light Sensor", unit="lux")
    pressure_sensor = PressureSensor(sensor_id="P1", name="Pressure Sensor", unit="hPa")

    # Rejestracja wysyłania do serwera
    temp_sensor.register_callback(send_to_server)
    hum_sensor.register_callback(send_to_server)
    light_sensor.register_callback(send_to_server)
    pressure_sensor.register_callback(send_to_server)

    try:
        for _ in range(10):
            temp_sensor.read_value()
            hum_sensor.read_value()
            light_sensor.read_value()
            pressure_sensor.read_value()
            time.sleep(1)

    finally:
        client.close()
        logger.stop()
        print("Zakończono wysyłanie danych.")

if __name__ == "__main__":
    main()
