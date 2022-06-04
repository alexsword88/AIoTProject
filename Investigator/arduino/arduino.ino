#define E1 5
#define E2 6
#define M1 4
#define M2 7
#define SPEED_STEP 10

int SPEED = 0;

void clearSerial(){
  while(Serial.available()){
    Serial.read();
  }
}

void speedUp() {
  SPEED = min(SPEED + SPEED_STEP, 255);
  analogWrite(E1, SPEED);
  analogWrite(E2, SPEED);
}

void speedDown() {
  SPEED = max(SPEED - SPEED_STEP, 0);
  analogWrite(E1, SPEED);
  analogWrite(E2, SPEED);
}

void brake() {
  SPEED = 0;
  digitalWrite(E1, SPEED);
  digitalWrite(M1, LOW);
  digitalWrite(E2, SPEED);
  digitalWrite(M2, LOW);
}

void forward() {
  speedUp();
  digitalWrite(M1, HIGH);
  digitalWrite(M2, HIGH);
}

void back() {
  speedUp();
  digitalWrite(M1, LOW);
  digitalWrite(M2, LOW);
}

void left() {
  speedUp();
  digitalWrite(M1, LOW);
  digitalWrite(M2, HIGH);
}

void right() {
  speedUp();
  digitalWrite(M1, HIGH);
  digitalWrite(M2, LOW);
}

void setup(void)
{
  int i;
  for (i = 4; i <= 7; i++)
    pinMode(i, OUTPUT);
  Serial.begin(115200);
  brake();
}

void loop(void)
{
  if (Serial.available()) {
    char val = Serial.read();
    switch (val)
    {
      case 'w'://Move Forward
        forward();  //move forward in max speed
        break;
      case 's'://Move Backward
        back();  //move back in max speed
        break;
      case 'a'://Turn Left
        left();
        break;
      case 'd'://Turn Right
        right();
        break;
      case 'x':
        brake();
        break;
    }
    clearSerial();
  } else {
    speedDown();
  }
  delay(500);
}
