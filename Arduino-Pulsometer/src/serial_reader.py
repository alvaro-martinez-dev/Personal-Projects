import serial
import time

class SerialReader:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        time.sleep(2)  # el Arduino se resetea al abrir el puerto serie, hay que esperar
        return self.connection

    def read_value(self):
        """Lee una línea y la devuelve como int. Devuelve None si falla el parseo."""
        if self.connection is None:
            raise RuntimeError("Conexión no iniciada. Llama a connect() primero.")
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
    reader = SerialReader(port="COM6")  # ajusta al puerto que detectaste
    reader.connect()
    try:
        while True:
            value = reader.read_value()
            if value is not None:
                print(value)
    except KeyboardInterrupt:
        reader.close()