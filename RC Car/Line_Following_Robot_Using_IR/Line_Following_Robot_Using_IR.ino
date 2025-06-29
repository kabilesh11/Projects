const int motorA_IN1 = D4;
const int motorA_IN2 = D3;
const int motorB_IN3 = D8;
const int motorB_IN4 = D7;
const int motorA_ENA = D2;
const int motorB_ENB = D5;

const int leftSensor = D0;
const int rightSensor = D1;

void setup() {
  pinMode(motorA_IN1, OUTPUT);
  pinMode(motorA_IN2, OUTPUT);
  pinMode(motorB_IN3, OUTPUT);
  pinMode(motorB_IN4, OUTPUT);
  pinMode(motorA_ENA, OUTPUT);
  pinMode(motorB_ENB, OUTPUT);
  pinMode(leftSensor, INPUT);
  pinMode(rightSensor, INPUT);

  stopMotors();
}

void loop() {
  int Statel = digitalRead(leftSensor);
  int Stater = digitalRead(rightSensor);

  if (Statel == LOW && Stater == LOW) {
    moveForward();
  } 
  else if (Statel == HIGH && Stater == LOW) {
    turnRight();
  }
  else if (Statel == LOW && Stater == HIGH) {
    turnLeft();
  }
  else {
    stopMotors();
  }
}

void moveForward() {
  digitalWrite(motorA_IN1, HIGH);
  digitalWrite(motorA_IN2, LOW);
  digitalWrite(motorB_IN3, HIGH);
  digitalWrite(motorB_IN4, LOW);
  analogWrite(motorA_ENA, 250);
  analogWrite(motorB_ENB, 250);
}

void turnRight() {
  digitalWrite(motorA_IN1, HIGH);
  digitalWrite(motorA_IN2, LOW);
  digitalWrite(motorB_IN3, LOW);
  digitalWrite(motorB_IN4, HIGH);
  analogWrite(motorA_ENA, 250);
  analogWrite(motorB_ENB, 250);
}

void turnLeft() {
  digitalWrite(motorA_IN1, LOW);
  digitalWrite(motorA_IN2, HIGH);
  digitalWrite(motorB_IN3, HIGH);
  digitalWrite(motorB_IN4, LOW);
  analogWrite(motorA_ENA, 250);
  analogWrite(motorB_ENB, 250);
}

void stopMotors() {
  digitalWrite(motorA_IN1, LOW);
  digitalWrite(motorA_IN2, LOW);
  digitalWrite(motorB_IN3, LOW);
  digitalWrite(motorB_IN4, LOW);
  analogWrite(motorA_ENA, 0);
  analogWrite(motorB_ENB, 0);
}
