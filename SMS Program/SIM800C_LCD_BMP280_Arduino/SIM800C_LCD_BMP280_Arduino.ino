#include <Wire.h>
#include <SPI.h>
#include <Adafruit_BMP280.h>
#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>

#define BMP280_ADDRESS 0x76

SoftwareSerial gsmSerial(9, 10);
LiquidCrystal_I2C lcd(0x27, 16, 2);  
Adafruit_BMP280 bmp; // I2C

void setup() {
  lcd.init();   
  lcd.backlight();  
  gsmSerial.begin(9600); 
  Serial.begin(9600);   
  
  Serial.begin(9600);
  while ( !Serial ) delay(100);  
  Serial.println(F("BMP280 test"));
  unsigned status;
  status = bmp.begin(BMP280_ADDRESS);
  if (!status) {
    Serial.println(F("Could not find a valid BMP280 sensor, check wiring or "
                      "try a different address!"));
    Serial.print("SensorID was: 0x"); 
    Serial.println(bmp.sensorID(),16);
    Serial.print("        ID of 0xFF probably means a bad address, a BMP 180 or BMP 085\n");
    Serial.print("   ID of 0x56-0x58 represents a BMP 280,\n");
    Serial.print("        ID of 0x60 represents a BME 280.\n");
    Serial.print("        ID of 0x61 represents a BME 680.\n");
    while (1) delay(10);
  }
 /* Default settings from the datasheet. */
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,   
                  Adafruit_BMP280::SAMPLING_X2,    
                  Adafruit_BMP280::SAMPLING_X16,    
                  Adafruit_BMP280::FILTER_X16, 
                  Adafruit_BMP280::STANDBY_MS_500); 
}
void loop() {
    Serial.print(F("Temperature = "));
    Serial.print(bmp.readTemperature());
    Serial.println((char)223);
    Serial.print(F("Pressure = "));
    Serial.print(bmp.readPressure());
    Serial.println(" Pa");
    Serial.print(F("Approx altitude = "));
    Serial.print(bmp.readAltitude(1013.25));
    Serial.println(" m");
    Serial.println();
    delay(20000);
    
    lcd.clear();
    lcd.setCursor(0, 0);   
    lcd.print("Temperature=");
    lcd.print(bmp.readTemperature()); 
    lcd.print((char)223);  
    lcd.print("C");
    lcd.setCursor(0, 1); 
    lcd.print("Pressure=");
    lcd.print(bmp.readPressure());
    lcd.print((char)223);      
    lcd.print("F");
    delay(500);
    for (int i = 0; i < 16; ++i) {
    lcd.scrollDisplayLeft();
    delay(600);
  }
  for (int i = 0; i < 16; ++i) {
    lcd.scrollDisplayRight();
    delay(600);
  }
    SendMessage(bmp.readTemperature(), bmp.readPressure(), bmp.readAltitude(1013.25));
    delay(1000);

  if (bmp.readTemperature()> 35){
    makecall()
  }
}

void SendMessage(float temperature, float pressure, float altitude) {
  gsmSerial.println("AT"); 
  delay(1000);
  if (gsmSerial.find("OK")) {
    gsmSerial.println("AT+CMGF=1"); 
    delay(1000);
    gsmSerial.print("AT+CMGS=\"+918220740768\""); 
    gsmSerial.write((byte)0x0D); 
    delay(1000);
    gsmSerial.write((byte)0x0A); 
    delay(1000);
    gsmSerial.print("Temperature: ");
    gsmSerial.print(temperature);
    gsmSerial.write((byte)0x0D); 
    delay(1000);
    gsmSerial.write((byte)0x0A); 
    delay(1000);
    gsmSerial.print("Pressure: ");
    gsmSerial.print(pressure);
    gsmSerial.write((byte)0x0D); 
    delay(1000);
    gsmSerial.write((byte)0x0A); 
    delay(1000);
    gsmSerial.print("Altitude: ");
    gsmSerial.print(altitude);
    gsmSerial.write((byte)0x0D); 
    delay(1000);
    gsmSerial.write((byte)0x0A); 
    delay(1000);
    gsmSerial.println((char)26); 
    delay(1000);
  }
}

void makecall(){
  gsmSerial.println("ATD+91xxxxxxxxxx;"); // Replace the number with the desired phone number
  Serial.println("Calling..."); // Print response over the serial port
  delay(1000);
}
