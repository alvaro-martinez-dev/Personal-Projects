README for the Arduino Pulsometer.

Hardware:
    - Arduino UNO
    - HALJIA Heart Rate Pulsometer Arduino Raspberry Pi (x2)
    - Breadboard
    - USB 2.0 high speed cable

Pulsometer physical connections to the ARDUINO:
    - Sensor(+) to Breadboard(+) to Arduino(5V) 
    - Sensor(-) to Arduino(GND)
    - Sensor(S) to Arduino(A0) and Arduino(A1)

PlatformIO (important): 
    1. Install PlatformIO IDE extension
    2. Restart VSCode
    3. Tap on the PlatformIO symbol, on the left sidebar, and press "Build" and check that everything is working
    4. Press "Upload" to upload it to the arduino
    5. If everything is wotking fine, close this window and open your project again. 
    6. Then run "python .\Arduino-Pulsometer\src\serial_reader.py" to see that the Arduino is being detected. 