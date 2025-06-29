#include <SoftwareSerial.h>

SoftwareSerial sim800c(9, 10); // RX, TX

#define PIR_PIN 2

void setup() {
  pinMode(PIR_PIN, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  sim800c.begin(9600);
  delay(1000);
}

void loop() {
  int pirState = digitalRead(PIR_PIN);
  
  if (pirState == HIGH) {
    digitalWrite(LED_BUILTIN, HIGH); // Turn on built-in LED
    makeCall();
    delay(5000); // Delay to avoid multiple triggers
  } else {
    digitalWrite(LED_BUILTIN, LOW); // Turn off built-in LED
  }
}

void makeCall() {
  sim800c.println("ATD+917305800719;"); // Replace the number with the desired phone number
  Serial.println("Calling..."); // Print response over the serial port
  delay(1000);
}
