const int motorA_IN1 = 2;
const int motorA_IN2 = 3;
const int motorB_IN3 = 4;
const int motorB_IN4 = 5;
const int motorA_ENA = 6;
const int motorB_ENB = 7;

const int leftSensor = 9;
const int rightSensor = 10;

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
  analogWrite(motorA_ENA, 100); // Adjust speed if needed
  analogWrite(motorB_ENB, 100); // Adjust speed if needed
}

void turnRight() {
  digitalWrite(motorA_IN1, HIGH);
  digitalWrite(motorA_IN2, LOW);
  digitalWrite(motorB_IN3, LOW);
  digitalWrite(motorB_IN4, HIGH);
  analogWrite(motorA_ENA, 100);
  analogWrite(motorB_ENB, 100);
}

void turnLeft() {
  digitalWrite(motorA_IN1, LOW);
  digitalWrite(motorA_IN2, HIGH);
  digitalWrite(motorB_IN3, HIGH);
  digitalWrite(motorB_IN4, LOW);
  analogWrite(motorA_ENA, 100);
  analogWrite(motorB_ENB, 100);
}

void stopMotors() {
  digitalWrite(motorA_IN1, LOW);
  digitalWrite(motorA_IN2, LOW);
  digitalWrite(motorB_IN3, LOW);
  digitalWrite(motorB_IN4, LOW);
  analogWrite(motorA_ENA, 0);
  analogWrite(motorB_ENB, 0);
}
