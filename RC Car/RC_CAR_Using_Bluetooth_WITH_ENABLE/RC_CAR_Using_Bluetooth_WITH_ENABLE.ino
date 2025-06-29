#include <SoftwareSerial.h>

SoftwareSerial BTSerial(10, 11); // RX, TX

const int motorA_IN1 = 7;
const int motorA_IN2 = 8;
const int motorB_IN3 = 9;
const int motorB_IN4 = 10;

void setup() {
  BTSerial.begin(9600);
  Serial.begin(9600);

  pinMode(motorA_IN1, OUTPUT);
  pinMode(motorA_IN2, OUTPUT);
  pinMode(motorB_IN3, OUTPUT);
  pinMode(motorB_IN4, OUTPUT);

  stopMotors();
}

void loop() {
  if (BTSerial.available()) {
    char command = BTSerial.read();
    Serial.println(command);

    switch (command) {
      case 'F': // Move Forward
        moveForward();
        break;
      case 'B': // Move Backward
        moveBackward();
        break;
      case 'L': // Turn Left
        turnLeft();
        break;
      case 'R': // Turn Right
        turnRight();
        break;
      case 'S': // Stop
        stopMotors();
        break;
      default:
        stopMotors();
        break;
    }
  }
}

void moveForward() {
  digitalWrite(motorA_IN1, HIGH);
  digitalWrite(motorA_IN2, LOW);
  digitalWrite(motorB_IN3, HIGH);
  digitalWrite(motorB_IN4, LOW);
}

void moveBackward() {
  digitalWrite(motorA_IN1, LOW);
  digitalWrite(motorA_IN2, HIGH);
  digitalWrite(motorB_IN3, LOW);
  digitalWrite(motorB_IN4, HIGH);
}

void turnLeft() {
  digitalWrite(motorA_IN1, LOW);
  digitalWrite(motorA_IN2, HIGH);
  digitalWrite(motorB_IN3, HIGH);
  digitalWrite(motorB_IN4, LOW);
}

void turnRight() {
  digitalWrite(motorA_IN1, HIGH);
  digitalWrite(motorA_IN2, LOW);
  digitalWrite(motorB_IN3, LOW);
  digitalWrite(motorB_IN4, HIGH);
}

void stopMotors() {
  digitalWrite(motorA_IN1, LOW);
  digitalWrite(motorA_IN2, LOW);
  digitalWrite(motorB_IN3, LOW);
  digitalWrite(motorB_IN4, LOW);
}
