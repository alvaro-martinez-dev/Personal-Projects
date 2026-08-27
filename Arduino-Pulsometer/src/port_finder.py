import serial.tools.list_ports

DEFAULT_KEYWORDS = ["Arduino", "CH340", "USB-SERIAL", "USB2.0-Serial", "Dispositivo serie USB"]


def find_arduino_port(keywords=None):
    """
    Looks for the serial port with highest chance of being an Arduino device.
    This search is done looking for typical key words associated to the device.
    The name of the device or None gets printed out.
    """
    keywords = keywords or DEFAULT_KEYWORDS

    for port in serial.tools.list_ports.comports():
        if any(keyword.lower() in port.description.lower() for keyword in keywords):
            return port.device

    return None


def list_available_ports():
    return [(port.device, port.description) for port in serial.tools.list_ports.comports()]


if __name__ == "__main__":
    print("Available ports:")
    for device, description in list_available_ports():
        print(f"  {device} — {description}")

    detected = find_arduino_port()
    if detected:
        print(f"\nArduino detected in: {detected}")
    else:
        print("\nNo Arduino found automatically.")