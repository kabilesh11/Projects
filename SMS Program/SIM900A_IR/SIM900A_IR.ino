#include <SoftwareSerial.h>

SoftwareSerial sim900A(9, 10); // RX, TX

#define IR_PIN_1 A0  // Analog pin for IR sensor 1
#define IR_PIN_2 A1  // Analog pin for IR sensor 2

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  sim900A.begin(9600); // Corrected to sim900A
  delay(1000);
}

void loop() {
  int irValue1 = analogRead(IR_PIN_1);
  int irValue2 = analogRead(IR_PIN_2);
  
  if (irValue1 > 500 || irValue2 > 500) { // Adjust threshold value as per your IR sensor's sensitivity
    digitalWrite(LED_BUILTIN, HIGH); // Turn on built-in LED
    Message();
    delay(5000); // Delay to avoid multiple triggers
  } else {
    digitalWrite(LED_BUILTIN, LOW); // Turn off built-in LED
  }
}

void Message() {
  sim900A.println("AT+CMGF=1");    //Sets the GSM Module in Text Mode
  delay(1000);  // Delay of 1 second
  sim900A.println("AT+CMGS=\"+918220740768\""); // Replace with recipient's mobile number
  delay(1000);
  sim900A.print("Motion Detected"); // The SMS text you want to send
  sim900A.write(26); // ASCII code of CTRL+Z
  delay(1000); // Wait for the "OK" response
}
