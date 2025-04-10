void setup() {
  // Set motor control pins as outputs
  pinMode(2, OUTPUT);  // Left motors forward
  pinMode(3, OUTPUT);  // Left motors reverse
  pinMode(4, OUTPUT);  // Right motors forward
  pinMode(5, OUTPUT);  // Right motors reverse
}

void loop() {
  // Set motor directions
  digitalWrite(2, LOW);  // Left motors forward
  digitalWrite(3, HIGH);   // Left motors reverse (off)
  digitalWrite(4, LOW);  // Right motors forward
  digitalWrite(5, HIGH);   // Right motors reverse (off)
}
