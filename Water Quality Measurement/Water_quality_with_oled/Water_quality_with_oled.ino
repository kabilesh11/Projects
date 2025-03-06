#define BLYNK_TEMPLATE_ID "TMPL3JPfFwhTF"
#define BLYNK_TEMPLATE_NAME "Notification and Datas"
#define BLYNK_AUTH_TOKEN "mSScGyu1sMawcXXOStY1KpuQRYYJ7q6W"

#include <BlynkSimpleEsp8266.h>
#include <ESP8266WiFi.h>
#include <Wire.h>                 // Required for I2C communication
#include <Adafruit_SSD1306.h>     // Required for OLED display
#include <OneWire.h>              // DS18B20 OneWire library
#include <DallasTemperature.h>    // DS18B20 Temperature sensor library

// WiFi Credentials
char auth[] = "mSScGyu1sMawcXXOStY1KpuQRYYJ7q6W";
char ssid[] = "admin";
char pass[] = "88888888";

// Sensor Pin Configurations
#define ONE_WIRE_BUS D3   // DS18B20 Temperature Sensor on D3
#define PH_SENSOR A0      // pH sensor on A0

// OLED Display Settings
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// OneWire and DallasTemperature Setup
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Sensor Calibration Factors
float AREF = 3.3;       // ESP8266 ADC Reference Voltage
float ecCalibration = 1; // EC Sensor Calibration Factor

void setup() {
  Serial.begin(115200);
  Blynk.begin(auth, ssid, pass);

  // Initialize OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }
  display.display();  
  delay(2000); // Pause for 2 seconds to show initial screen

  // Initialize DS18B20 Temperature Sensor
  sensors.begin();
}

void loop() {
  Blynk.run();

  // Get Temperature from DS18B20
  sensors.requestTemperatures();
  float waterTemp = sensors.getTempCByIndex(0);

  // Read EC Value (Assuming a basic EC sensor using ADC)
  float rawEc = analogRead(A0) * AREF / 1024.0;
  float tempCompensation = 1.0 + 0.02 * (waterTemp - 25.0);
  float ecValue = (rawEc / tempCompensation) * ecCalibration;

  // Read pH Value (Using a proper voltage conversion method)
  int rawPhValue = analogRead(PH_SENSOR);
  float voltage = (rawPhValue * AREF) / 1023.0;  // Convert ADC value to voltage
  float phValue = 3.5 * voltage;  // Adjust this based on calibration

  // Debugging Output
  Serial.print(F("EC: ")); Serial.println(ecValue, 2);
  Serial.print(F("Temperature: ")); Serial.println(waterTemp, 2);
  Serial.print(F("pH: ")); Serial.println(phValue, 2);

  // Send Data to Blynk App
  Blynk.virtualWrite(V1, ecValue);     // EC value
  Blynk.virtualWrite(V2, phValue);     // pH value
  Blynk.virtualWrite(V3, waterTemp);   // Temperature value

  // Display Data on OLED
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print(F("EC: ")); display.print(ecValue, 2);

  display.setCursor(0, 20);
  display.print(F("Temp: ")); display.print(waterTemp, 2);

  display.setCursor(0, 40);
  display.print(F("pH: ")); display.print(phValue, 2);

  display.display();  // Update OLED

  delay(1000);  // Wait for next sensor reading
}
