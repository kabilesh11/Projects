#define BLYNK_TEMPLATE_ID "TMPL3OblLn5f2"
#define BLYNK_TEMPLATE_NAME "Quickstart Template"
#define BLYNK_AUTH_TOKEN "DGtHlKFrPJb2fyxmrMOpHiD-K42bcKWM"
#define BLYNK_PRINT Serial

#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <ESP8266HTTPClient.h> // Include the HTTP client library

// Pushover credentials
const char* pushoverToken = "agybfkvc5u8ys3d53fz1bnk6u38i7q";
const char* pushoverUser = "uhzs5zj6u2rwsawborxmt4tmr76t95";

char auth[] = "DGtHlKFrPJb2fyxmrMOpHiD-K42bcKWM"; // Enter your Blynk authentication token here
char ssid[] = "_C_M_";
char pass[] = "00000000";

// Analog input pin for ACS712 sensor
const int sensorPin = A0;

float lastSensorReading = 0.0;

// Initialize WiFiClient object
WiFiClient client;

void setup() {
  Serial.begin(115200);
  Blynk.begin(auth, ssid, pass);
}

void loop() {
  Blynk.run();
  float current = getCurrentReading();
  Blynk.virtualWrite(V1, current); // Send current reading to virtual pin V1 on the Blynk app
}

float getCurrentReading() {
  int sensorValue = analogRead(sensorPin);
  float voltage = sensorValue * (3.3 / 1023.0); // Adjusted voltage calculation for ESP8266 ADC
  float current = (voltage - 2.5) / 0.185; // ACS712 sensitivity: 185mV/A
  
  float difference = abs(current - lastSensorReading);
  lastSensorReading = current;

  if (difference > 0.3) {
    Serial.println("Power theft detected!");
    sendPushNotification("Power theft detected!");
  } else {
    Serial.println("No power theft detected");
  }

  return current;
}

void sendPushNotification(String message) {
  HTTPClient http;
  http.begin(client, "https://api.pushover.net/1/messages.json");
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");

  String postData = "token=" + String(pushoverToken) + "&user=" + String(pushoverUser) + "&message=" + message;
  int httpResponseCode = http.POST(postData);

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("Pushover API response code: ");
    Serial.println(httpResponseCode);
    Serial.print("Response: ");
    Serial.println(response);
  } else {
    Serial.print("Error sending Pushover notification. HTTP error code: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}
