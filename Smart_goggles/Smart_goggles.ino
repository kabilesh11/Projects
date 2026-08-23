const int trigPin = 8;
const int echoPin = 7;
long duration;
int distanceCm, distanceInch;
void setup()
{ 

 Serial.begin(9600); 
 pinMode(trigPin, OUTPUT);
 pinMode(echoPin, INPUT);
 pinMode(12, OUTPUT); // Connect Buzzer Pin D5

}
void loop()
{
digitalWrite(trigPin, LOW);
delayMicroseconds(2);
digitalWrite(trigPin, HIGH);
delayMicroseconds(10);
digitalWrite(trigPin, LOW);
duration = pulseIn(echoPin, HIGH);
distanceCm= duration*0.034/2;
distanceInch = duration*0.0133/2;
Serial.println("Distance: ");
Serial.println(distanceCm);
delay (100);
// See the Ultrasonic Sensor Value in Serial Monitor



if(distanceCm < 25)  // You can Change the value 
{
  
  digitalWrite(12, HIGH);  // Buzzer O
  
}

else
{
    digitalWrite(12,LOW);  // Buzzer OFF
}
}