// IMPORTANT: INSTALL PLATFORMIO IDE EXTENSION 
// main.cpp reads sensor. Equivalent to .ino file, but with the PlatformIO IDE extension this is the way to go. 

// src/main.cpp (PlatformIO)
#include <Arduino.h>  // Needs to be included. Arduino IDE does it by defect, but platformIO doesn't

const int SENSOR_PIN = A0;
const int BAUD_RATE = 9600;
const int SAMPLE_DELAY_MS = 10;

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(SENSOR_PIN, INPUT);
}

void loop() {
  int sensorValue = analogRead(SENSOR_PIN);
  Serial.println(sensorValue);
  delay(SAMPLE_DELAY_MS);
}