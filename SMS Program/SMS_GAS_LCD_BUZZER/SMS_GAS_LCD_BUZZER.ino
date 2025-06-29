#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>

// Initialize I2C LCD
LiquidCrystal_I2C lcd(0x27, 16, 2); // I2C address 0x27, 16 columns and 2 rows
//SDA: Connect to A4 on the Arduino Uno.
//SCL: Connect to A5 on the Arduino Uno.

// Initialize Software Serial for GSM
SoftwareSerial sim900A(9, 10); // RX, TX

int buzzer = 4;
int sensor = A0;
int sensorThresh = 400;

void setup()
{
  pinMode(buzzer, OUTPUT);
  pinMode(sensor, INPUT);
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  sim900A.begin(9600); // Start GSM serial communication
  delay(1000);
}

void loop()
{
  int analogValue = analogRead(sensor);
  Serial.print(analogValue);
  if (analogValue > sensorThresh)
  {
    tone(buzzer, 1000, 10000);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("ALERT");
    delay(700);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Gas Leakage");
    lcd.setCursor(0, 1);
    lcd.print("Detected");
    delay(700);
    Message();
  }
  else
  {
    noTone(buzzer);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("SAFE");
    delay(700);
    lcd.clear();
    lcd.setCursor(0, 1);
    lcd.print("ALL CLEAR");
    delay(700);
  }      
}

void Message() {
  sim900A.println("AT+CMGF=1");    // Set GSM Module to Text Mode
  delay(1000);  // Delay of 1 second
  sim900A.println("AT+CMGS=\"+919787777759\""); // Replace with recipient's mobile number
  delay(1000);
  sim900A.print("Gas Leakage Detected"); // The SMS text you want to send
  sim900A.write(26); // ASCII code of CTRL+Z
  delay(1000); // Wait for the "OK" response
}
