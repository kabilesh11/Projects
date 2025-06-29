// Define pin numbers
const int irSensorPin = 2;  // Pin connected to the IR sensor's OUT pin
const int relayPin = 3;     // Pin connected to the relay module's IN pin

// Variables to track timing
unsigned long relayOnTime = 0;
const unsigned long relayDelay = 10000; // 10 seconds delay

// State variables
bool relayActive = false;

void setup() {
  // Initialize the serial communication
  Serial.begin(9600);

  // Set the IR sensor pin as an input
  pinMode(irSensorPin, INPUT);
  
  // Set the relay pin as an output
  pinMode(relayPin, OUTPUT);
  
  // Ensure the relay is off initially
  digitalWrite(relayPin, LOW);
}

void loop() {
  // Read the state of the IR sensor
  int irSensorState = digitalRead(irSensorPin);
  
  // Print the sensor state to the Serial Monitor for debugging
  Serial.print("IR Sensor State: ");
  Serial.println(irSensorState);
  
  // If the IR sensor detects an object (usually HIGH when object is detected)
  if (irSensorState == HIGH) {
    // If the relay is not already active
    if (!relayActive) {
      // Turn on the relay and record the current time
      digitalWrite(relayPin, HIGH);
      relayOnTime = millis();
      relayActive = true;
      Serial.println("Object detected! Relay ON.");
    }
  } else {
    // If the object is no longer detected and the relay was active
    if (relayActive) {
      // Check if 10 seconds have passed since the relay was turned on
      if (millis() - relayOnTime >= relayDelay) {
        // Turn off the relay and reset state
        digitalWrite(relayPin, LOW);
        relayActive = false;
        Serial.println("Relay OFF after 10 seconds.");
      }
    }
  }
  
  // Add a small delay for stability
  delay(100);
}
