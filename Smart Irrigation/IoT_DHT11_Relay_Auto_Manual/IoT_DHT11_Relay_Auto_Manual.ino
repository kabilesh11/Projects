#define BLYNK_TEMPLATE_ID "TMPL3_2zH5NNA"
#define BLYNK_TEMPLATE_NAME "Smart Irrigation"
#define BLYNK_AUTH_TOKEN "YyrujXg6x2T7fFoaVe4Apg1vjBO9t1pg"

#define BLYNK_PRINT Serial
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <SimpleDHT.h>

char auth[] = "YyrujXg6x2T7fFoaVe4Apg1vjBO9t1pg"; // Get this from the Blynk app
char ssid[] = "admin";
char pass[] = "11111111";

#define DHTPIN D5
#define DHTTYPE DHT11

SimpleDHT11 dht(DHTPIN);

const int moisturePin = A0;  // Pin connected to the analog output of the soil moisture sensor
const int relayPin = D8;     // Pin connected to the relay module
int moistureValue = 0;       // Variable to store the moisture value

// Define the threshold values for soil moisture
const int lowerThreshold = 600;  // Lower threshold to start watering
const int upperThreshold = 1000; // Upper threshold to stop watering

BlynkTimer timer;

void setup() {
  Serial.begin(9600);           // Initialize serial communication for debugging
  Blynk.begin(auth, ssid, pass);
  
  pinMode(moisturePin, INPUT);  // Set the moisture sensor pin as an input
  pinMode(relayPin, OUTPUT);    // Set the relay pin as an output
  digitalWrite(relayPin, LOW);  // Ensure the relay is off at startup
  
  timer.setInterval(2000L, sendSensorData);
}

void loop() {
  Blynk.run();
  timer.run();
}

void sendSensorData() {
  byte temperature = 0;
  byte humidity = 0;
  moistureValue = analogRead(moisturePin); // Read the analog value from the sensor

  int err = dht.read(&temperature, &humidity, NULL);
  if (err != SimpleDHTErrSuccess) {
    Serial.print("Read DHT11 failed, err="); Serial.println(err);
    return;
  }

  Blynk.virtualWrite(V1, (int)temperature);
  Blynk.virtualWrite(V2, (int)humidity);
  Blynk.virtualWrite(V3, moistureValue);

  // Check if the soil moisture is below the lower threshold
  if (moistureValue < lowerThreshold) {
    digitalWrite(relayPin, HIGH); // Turn on the relay to start the water pump
    Serial.println("Watering the plant...");
    Blynk.virtualWrite(V4, 1); // Notify the app
  } 
  // Check if the soil moisture is at or above the upper threshold
  else if (moistureValue >= upperThreshold) {
    digitalWrite(relayPin, LOW);  // Turn off the relay to stop the water pump
    Serial.println("Soil is moist enough.");
    Blynk.virtualWrite(V4, 0); // Notify the app
  }
}

BLYNK_WRITE(V5) { // Control relay from the app button
  int pinValue = param.asInt();
  if (pinValue) {
    digitalWrite(relayPin, HIGH); // Turn on the water pump
  } else {
    digitalWrite(relayPin, LOW); // Turn off the water pump
  }
}
