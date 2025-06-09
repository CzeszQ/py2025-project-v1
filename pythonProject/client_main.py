from Logger import Logger
from TemperatureSensor import TemperatureSensor
from HumiditySensor import HumiditySensor
from LightSensor import LightSensor
from PressureSensor import PressureSensor
from network.Client import Client
from datetime import datetime
import time


def main():
    logger = Logger("config.json")
    logger.start()

    client = Client("localhost", 5000, logger=logger)

    sensors = [
        TemperatureSensor("T1", "Temp Sensor", "°C"),
        HumiditySensor("H1", "Humidity Sensor", "%"),
        LightSensor("L1", "Light Sensor", "lux"),
        PressureSensor("P1", "Pressure Sensor", "hPa")
    ]

    try:
        for iteration in range(10):
            for sensor in sensors:
                # Sprawdź czy połączenie nie zostało przerwane
                if client.is_connection_failed():
                    print("Przerywanie działania - połączenie z serwerem niemożliwe")
                    logger.log_error("Przerywanie działania - połączenie z serwerem niemożliwe")
                    return

                value = sensor.read_value()
                reading = {
                    "timestamp": datetime.now(),
                    "sensor_id": sensor.sensor_id,
                    "value": value,
                    "unit": sensor.unit
                }
                logger.log_reading(**reading)

                reading_to_send = reading.copy()
                reading_to_send["timestamp"] = reading_to_send["timestamp"].isoformat()

                # Próba wysłania danych
                success = client.send(reading_to_send)
                if not success and client.is_connection_failed():
                    print("Przerywanie działania - nie udało się nawiązać połączenia po 3 próbach")
                    logger.log_error("Przerywanie działania - nie udało się nawiązać połączenia po 3 próbach")
                    return

            time.sleep(1)

    except KeyboardInterrupt:
        print("Przerwano przez użytkownika")
        logger.log_info("Przerwano przez użytkownika")
    finally:
        client.close()
        logger.stop()
        print("Zakończono działanie klienta.")


if __name__ == "__main__":
    main()
