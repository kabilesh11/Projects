#include <SoftwareSerial.h>
SoftwareSerial mySerial(9, 10);

const int motionSensorPin = 2; // Assuming motion sensor is connected to pin 2
bool motionDetected = false;

enum State {
  IDLE,
  MOTION_DETECTED,
  SENDING_MESSAGE
};

State currentState = IDLE;

void setup() {
  pinMode(motionSensorPin, INPUT);
  mySerial.begin(9600);
  Serial.begin(9600);
  Serial.println("Motion Detection SMS System");
  delay(100);
}

void loop() {
  switch (currentState) {
    case IDLE:
      if (digitalRead(motionSensorPin) == HIGH) {
        currentState = MOTION_DETECTED;
      }
      break;
      
    case MOTION_DETECTED:
      SendMessage();
      currentState = SENDING_MESSAGE;
      break;
      
    case SENDING_MESSAGE:
      if (mySerial.available() > 0) {
        Serial.write(mySerial.read());
      }
      // You can add additional handling here if needed
      break;
  }
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
