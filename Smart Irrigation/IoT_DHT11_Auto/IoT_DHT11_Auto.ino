#define BLYNK_TEMPLATE_ID "TMPL3pb6ZRUDV"
#define BLYNK_TEMPLATE_NAME "Smart Irrigation"
#define BLYNK_AUTH_TOKEN "9CR-NFRUHWwelJVdpNiO4zVfC_xfF9ci"

#define BLYNK_PRINT Serial
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <SimpleDHT.h>

char auth[] = "YyrujXg6x2T7fFoaVe4Apg1vjBO9t1pg"; // Get this from the Blynk app
char ssid[] = "admin";
char pass[] = "adminadmin";

#define DHTPIN D5
#define DHTTYPE DHT11

SimpleDHT11 dht(DHTPIN);


BlynkTimer timer;

void setup() {
  Serial.begin(9600);           // Initialize serial communication for debugging
  Blynk.begin(auth, ssid, pass);

  
  timer.setInterval(2000L, sendSensorData);
}
void loop() {

  Blynk.run();
  timer.run();
}

void sendSensorData() {
  byte temperature = 0;
  byte humidity = 0;

  int err = dht.read(&temperature, &humidity, NULL);
  if (err != SimpleDHTErrSuccess) {
    Serial.print("Read DHT11 failed, err="); Serial.println(err);
    return;
  }

  Blynk.virtualWrite(V1, (int)temperature);
  Blynk.virtualWrite(V2, (int)humidity);
}