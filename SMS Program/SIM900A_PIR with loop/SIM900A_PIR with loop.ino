#include <SoftwareSerial.h>
SoftwareSerial mySerial(9, 10);

const int motionSensorPin = 2; // Assuming motion sensor is connected to pin 2
bool motionDetected = false;

void setup() {
  pinMode(motionSensorPin, INPUT);
  mySerial.begin(9600);
  Serial.begin(9600);
  Serial.println("Motion Detection SMS System");
  delay(100);
}

void loop() {
  if (digitalRead(motionSensorPin) == HIGH) {
    if (!motionDetected) { // Check if motion was not previously detected
      SendMessage();
      motionDetected = true; // Set motion detected flag
    }
  } else {
    motionDetected = false; // Reset motion detected flag
  }

  if (mySerial.available() > 0)
    Serial.write(mySerial.read());
}

void SendMessage() {
  mySerial.println("AT+CMGF=1");
  delay(1000);
  mySerial.println("AT+CMGS=\"+918220740768\"\r");
  delay(1000);
  mySerial.println("Motion detected!"); // Message indicating motion detection
  delay(100);
  mySerial.println((char)26);
  delay(1000);
}
