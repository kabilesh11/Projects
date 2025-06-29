#include <SoftwareSerial.h>

SoftwareSerial mySerial(7, 8);

void setup() {
  mySerial.begin(9600);   // Setting the baud rate of GSM Module  
  Serial.begin(9600);    // Setting the baud rate of Serial Monitor (Arduino)
  Serial.println("GSM SIM900A BEGIN");
  Serial.println("Enter character for control option:");
  Serial.println("s : to send message");
  Serial.println("c : to make a call");
  Serial.println();
}

void loop() {
  if (Serial.available() > 0) {
    char option = Serial.read();
    switch (option) {
      case 's':
        SendMessage();
        break;
      case 'c':
        MakeCall();
        break;
    }
  }
}

void SendMessage() {
  mySerial.println("AT+CMGF=1");    //Sets the GSM Module in Text Mode
  delay(1000);  // Delay of 1 second
  mySerial.println("AT+CMGS=\"+917825062937\""); // Replace with recipient's mobile number
  delay(1000);
  mySerial.print("sim900a sms"); // The SMS text you want to send
  delay(100);
  mySerial.write(26); // ASCII code of CTRL+Z
  delay(1000);
}

void MakeCall() {
  mySerial.println("ATD+917825062937;"); // ATDxxxxxxxxxx; -- watch out here for semicolon at the end!!
  Serial.println("Calling +917825062937"); // print response over serial port
  delay(1000);
}
