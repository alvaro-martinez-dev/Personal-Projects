import serial
import time
from .port_finder import find_arduino_port

class SerialReader:
    def __init__(self, port=None, baudrate=9600, timeout=1, port_keywords=None):
        self.port = port or find_arduino_port(keywords=port_keywords)
        if self.port is None:
            raise RuntimeError("No Arduino device has been detected. Specify it manually.")
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        time.sleep(2)
        return self.connection

    def read_values(self):
        """Lee una línea con dos valores separados por coma. Devuelve (v1, v2) o None si falla."""
        if self.connection is None:
            raise RuntimeError("Connection not started. Call connect() first.")
        line = self.connection.readline().decode("utf-8", errors="ignore").strip()
        if not line:
            return None
        try:
            v1_str, v2_str = line.split(",")
            return int(v1_str), int(v2_str)
        except (ValueError, IndexError):
            return None

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()


if __name__ == "__main__":
    reader = SerialReader()
    reader.connect()
    try:
        while True:
            values = reader.read_values()
            if values is not None:
                v1, v2 = values
                print(f"Sensor 1: {v1}  |  Sensor 2: {v2}")
    except KeyboardInterrupt:
        reader.close()