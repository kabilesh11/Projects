const int moisturePin = A0; // Pin connected to the analog output of the soil moisture sensor
const int relayPin = 8;     // Pin connected to the relay module
int moistureValue = 0;      // Variable to store the moisture value

// Define the threshold values for soil moisture
const int lowerThreshold = 600;  // Lower threshold to start watering
const int upperThreshold = 1000; // Upper threshold to stop watering

void setup() {
  Serial.begin(9600);       // Initialize serial communication for debugging
  pinMode(moisturePin, INPUT); // Set the moisture sensor pin as an input
  pinMode(relayPin, OUTPUT);   // Set the relay pin as an output
  digitalWrite(relayPin, LOW); // Ensure the relay is off at startup
}

void loop() {
  moistureValue = analogRead(moisturePin); // Read the analog value from the sensor
  Serial.print("Soil Moisture Level: ");
  Serial.println(moistureValue);          // Print the moisture value to the Serial Monitor

  // Check if the soil moisture is below the lower threshold
  if (moistureValue < lowerThreshold) {
    digitalWrite(relayPin, HIGH); // Turn on the relay to start the water pump
    Serial.println("Watering the plant...");
  } 
  // Check if the soil moisture is at or above the upper threshold
  else if (moistureValue >= upperThreshold) {
    digitalWrite(relayPin, LOW);  // Turn off the relay to stop the water pump
    Serial.println("Soil is moist enough.");
  }

  delay(1000); // Wait for 1 second before taking another reading
}
