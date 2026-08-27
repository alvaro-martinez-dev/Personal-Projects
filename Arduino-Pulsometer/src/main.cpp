// IMPORTANT: INSTALL PLATFORMIO IDE EXTENSION 
// main.cpp reads sensor. Equivalent to .ino file, but with the PlatformIO IDE extension this is the way to go. 

// src/main.cpp (PlatformIO)
#include <Arduino.h>

const int SENSOR_PIN_1 = A0;
const int SENSOR_PIN_2 = A1;
const int BAUD_RATE = 9600;
const int SAMPLE_DELAY_MS = 10;

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(SENSOR_PIN_1, INPUT);
  pinMode(SENSOR_PIN_2, INPUT);
}

void loop() {
  int value1 = analogRead(SENSOR_PIN_1);
  int value2 = analogRead(SENSOR_PIN_2);
  Serial.print(value1);
  Serial.print(",");
  Serial.println(value2);
  delay(SAMPLE_DELAY_MS);
}