#include <OneWire.h>
#include <DallasTemperature.h>
#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>

const int SENSOR_PIN = 13; 
SoftwareSerial mySerial(9, 10);

OneWire oneWire(SENSOR_PIN);         
DallasTemperature sensors(&oneWire); 
LiquidCrystal_I2C lcd(0x27, 16, 2);  

float tempCelsius;    // temperature in Celsius
float tempFahrenheit; // temperature in Fahrenheit

void setup()
{
  sensors.begin();    // initialize the sensor
  lcd.init();         // initialize the lcd
  lcd.backlight();    // open the backlight 
  
  
  mySerial.begin(9600);   // Setting the baud rate of GSM Module  
  Serial.begin(9600);    // Setting the baud rate of Serial Monitor (Arduino)
  
}

void loop()
{
  sensors.requestTemperatures();             // send the command to get temperatures
  tempCelsius = sensors.getTempCByIndex(0);  // read temperature in Celsius
  tempFahrenheit = tempCelsius * 9 / 5 + 32; // convert Celsius to Fahrenheit

  lcd.clear();
  lcd.setCursor(0, 0);       // start to print at the first row
  lcd.print(tempCelsius);    // print the temperature in Celsius
  lcd.print((char)223);      // print ° character
  lcd.print("C");
  lcd.setCursor(0, 1);       // start to print at the second row
  lcd.print(tempFahrenheit); // print the temperature in Fahrenheit
  lcd.print((char)223);      // print ° character
  lcd.print("F");
  delay(500);
  
  SendMessage();
  delay(60000);
}

void SendMessage()
{
  mySerial.println("AT+CMGF=1");    //Sets the GSM Module in Text Mode
  delay(1000);  // Delay of 1000 milli seconds or 1 second
  mySerial.println("AT+CMGS=\"+918220740768\" "); // Replace x with mobile number
  delay(1000);
  mySerial.println("Gas Leak");// The SMS text you want to send
  delay(1000);
  mySerial.println((char)26);// ASCII code of CTRL+Z
  delay(1000);
  mySerial.println(tempFahrenheit);// The SMS text you want to send
  delay(1000);
  mySerial.println((char)26);// ASCII code of CTRL+Z
  delay(1000);
}
