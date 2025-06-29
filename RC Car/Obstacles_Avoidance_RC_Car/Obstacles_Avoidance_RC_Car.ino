#include <Servo.h>

#define trigPin 9
#define echoPin 10
#define in1 4
#define in2 5
#define in3 6
#define in4 7
#define enA 3  // PWM pin for controlling motor A speed (changed from 8 to 3)
#define enB 11 // PWM pin for controlling motor B speed
#define servoPin 2  // Changed to pin 2 to avoid conflicts with PWM pins
#define motorSpeed 150 // Speed for motors (0-255)

Servo myservo;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  pinMode(enA, OUTPUT); // Set ENA as an output
  pinMode(enB, OUTPUT); // Set ENB as an output
  myservo.attach(servoPin);
  myservo.write(90);  // Set servo to initial position
  Serial.begin(9600);
}

void loop() {
  long duration, distance;

  // Trigger the ultrasonic sensor
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = (duration / 2) / 29.1;  // Convert to centimeters

  if (distance < 20) {
    // Obstacle detected, stop and turn
    stopCar();
    delay(500);
    turnRight();
    delay(1000);
  } else {
    moveForward();
  }
}

void moveForward() {
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(enA, motorSpeed);  // Control speed of motor A
  analogWrite(enB, motorSpeed);  // Control speed of motor B
}

void turnRight() {
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(enA, motorSpeed);  // Control speed of motor A
  analogWrite(enB, motorSpeed);  // Control speed of motor B
}

void stopCar() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
  analogWrite(enA, 0); // Stop motor A
  analogWrite(enB, 0); // Stop motor B
}
