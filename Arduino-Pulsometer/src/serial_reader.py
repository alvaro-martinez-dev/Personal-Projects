import serial
import time
from port_finder import find_arduino_port

class SerialReader:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port or find_arduino_port()
        if self.port is None:
            raise RuntimeError("No Arduino device has been detected. Specify it manually.")
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        time.sleep(2)  # Arduino gets reset when opening the serial port. You need to wait 
        return self.connection

    def read_value(self):
        """Lee una línea y la devuelve como int. Devuelve None si falla el parseo."""
        if self.connection is None:
            raise RuntimeError("Connection not started. Call connect() first.")
        line = self.connection.readline().decode("utf-8", errors="ignore").strip()
        if not line:
            return None
        try:
            return int(line)
        except ValueError:
            return None

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()


if __name__ == "__main__":
    reader = SerialReader() 
    reader.connect()
    try:
        while True:
            value = reader.read_value()
            if value is not None:
                print(value)
    except KeyboardInterrupt:
        reader.close()