#include <NewPing.h>
#include <Servo.h>

// Pin definitions
const int EN_A = D5;  // PWM pin for left motor speed control
const int EN_B = D6;  // PWM pin for right motor speed control
const int RightMotorForward = D2; // Right motor forward pin
const int LeftMotorForward = D3;  // Left motor forward pin
const int RightMotorBackward = D4; // Right motor backward pin
const int LeftMotorBackward = D7;  // Left motor backward pin
const int trig_pin = D0; // Ultrasonic sensor trigger pin
const int echo_pin = D1;

#define maximum_distance 200
boolean goesForward = false;
int distance = 100;
int motorSpeed = 70; // Set motor speed (0-255)

NewPing sonar(trig_pin, echo_pin, maximum_distance); // Ultrasonic sensor function
Servo servo_motor; // Servo motor

void setup() {
  pinMode(RightMotorForward, OUTPUT);
  pinMode(LeftMotorForward, OUTPUT);
  pinMode(LeftMotorBackward, OUTPUT);
  pinMode(RightMotorBackward, OUTPUT);
  pinMode(EN_A, OUTPUT);
  pinMode(EN_B, OUTPUT);

  servo_motor.attach(D0); // Servo motor control pin

  servo_motor.write(115);
  delay(2000);
  distance = readPing();
  delay(100);
  distance = readPing();
  delay(100);
  distance = readPing();
  delay(100);
  distance = readPing();
  delay(100);
}

void loop() {
  int distanceRight = 0;
  int distanceLeft = 0;
  delay(50);

  if (distance <= 20) {
    moveStop();
    delay(300);
    moveBackward();
    delay(300);
    moveStop();
    delay(300);
    distanceRight = lookRight();
    delay(300);
    distanceLeft = lookLeft();
    delay(300);

    if (distance >= distanceLeft) {
      turnRight();
      moveStop();
    } else {
      turnLeft();
      moveStop();
    }
  } else {
    moveForward(); 
  }
  distance = readPing();
}

int lookRight() {  
  servo_motor.write(50);
  delay(500);
  int distance = readPing();
  delay(100);
  servo_motor.write(115);
  return distance;
}

int lookLeft() {
  servo_motor.write(170);
  delay(500);
  int distance = readPing();
  delay(100);
  servo_motor.write(115);
  return distance;
}

int readPing() {
  delay(70);
  int cm = sonar.ping_cm();
  if (cm == 0) {
    cm = 250;
  }
  return cm;
}

void moveStop() {
  analogWrite(EN_A, 0);
  analogWrite(EN_B, 0);
}

void moveForward() {
  if (!goesForward) {
    goesForward = true;
    analogWrite(EN_A, motorSpeed);
    analogWrite(EN_B, motorSpeed);

    digitalWrite(LeftMotorForward, HIGH);
    digitalWrite(RightMotorForward, HIGH);
    digitalWrite(LeftMotorBackward, LOW);
    digitalWrite(RightMotorBackward, LOW);
  }
}

void moveBackward() {
  goesForward = false;
  analogWrite(EN_A, motorSpeed);
  analogWrite(EN_B, motorSpeed);

  digitalWrite(LeftMotorBackward, HIGH);
  digitalWrite(RightMotorBackward, HIGH);
  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(RightMotorForward, LOW);
}

void turnRight() {
  analogWrite(EN_A, motorSpeed);
  analogWrite(EN_B, motorSpeed);

  digitalWrite(LeftMotorForward, HIGH);
  digitalWrite(RightMotorBackward, HIGH);
  digitalWrite(LeftMotorBackward, LOW);
  digitalWrite(RightMotorForward, LOW);

  delay(500);

  digitalWrite(LeftMotorForward, HIGH);
  digitalWrite(RightMotorForward, HIGH);
  digitalWrite(LeftMotorBackward, LOW);
  digitalWrite(RightMotorBackward, LOW);
}

void turnLeft() {
  analogWrite(EN_A, motorSpeed);
  analogWrite(EN_B, motorSpeed);

  digitalWrite(LeftMotorBackward, HIGH);
  digitalWrite(RightMotorForward, HIGH);
  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(RightMotorBackward, LOW);

  delay(500);

  digitalWrite(LeftMotorForward, HIGH);
  digitalWrite(RightMotorForward, HIGH);
  digitalWrite(LeftMotorBackward, LOW);
  digitalWrite(RightMotorBackward, LOW);
}
