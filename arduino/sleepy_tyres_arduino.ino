int ledRed = 8;
int ledGreen = 9;
int buzzer = 7;

int in1 = 5;
int in2 = 6;
int ena = 10;

void setup() {
  pinMode(ledRed, OUTPUT);
  pinMode(ledGreen, OUTPUT);
  pinMode(buzzer, OUTPUT);

  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(ena, OUTPUT);

  Serial.begin(9600);

  // Set default direction
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();

    if (c == 'N') {  
      // Normal state
      digitalWrite(ledGreen, HIGH);
      digitalWrite(ledRed, LOW);
      digitalWrite(buzzer, LOW);
      analogWrite(ena, 200);  // motor speed normal
    } 
    else if (c == 'D') {  
      // Drowsy state
      digitalWrite(ledGreen, LOW);
      digitalWrite(ledRed, HIGH);
      digitalWrite(buzzer, HIGH);
      
      for (int speed = 200; speed >= 0; speed -= 10) {
      analogWrite(ena, speed);
      delay(250);
      }
      analogWrite(ena, 0);  // full stop
    }
  }
}