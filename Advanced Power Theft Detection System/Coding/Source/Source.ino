#define BLYNK_TEMPLATE_ID "TMPL3OblLn5f2"
#define BLYNK_TEMPLATE_NAME "Quickstart Template"
#define BLYNK_AUTH_TOKEN "DGtHlKFrPJb2fyxmrMOpHiD-K42bcKWM"

#define BLYNK_PRINT Serial
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>

char auth[] = "DGtHlKFrPJb2fyxmrMOpHiD-K42bcKWM"; // Enter your Blynk authentication token here
char ssid[] = "_C_M_";
char pass[] = "00000000";

// Analog input pin for ACS712 sensor
const int sensorPin = A0;

void setup() {
  Serial.begin(115200);
  Blynk.begin(auth, ssid, pass);
}

void loop() {
  Blynk.run();
  float current = getCurrentReading();
  Blynk.virtualWrite(V1, current); // Send current reading to virtual pin V1 on the Blynk app
  delay(1000); // Adjust delay as needed
}

float getCurrentReading() {
  int sensorValue = analogRead(sensorPin);
  float voltage = sensorValue * (3.3 / 1023.0); // Adjusted voltage calculation for ESP8266 ADC
  float current = (voltage - 2.5) / 0.185; // ACS712 sensitivity: 185mV/A
  return current;
}
