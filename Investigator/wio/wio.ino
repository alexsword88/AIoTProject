
#include <IRLibSendBase.h>
#include <IRLib_P01_NEC.h>
#include <IRLib_P02_Sony.h>
#include <IRLibCombo.h>
#include <math.h>

#define TEMP_SENSOR A0
#define B 4275
#define R0 100000

IRsend irSender;
int sendTemp = 0;

void clearSerial() {
  while (Serial.available()) {
    Serial.read();
  }
}

void waitAck() {
  while (true) {
    if (Serial.available()) {
      char ack[1];
      Serial.readBytes(ack, 1);
      if (ack[0] == '0') {
        break;
      }
    }
  }
  clearSerial();
}

void sendTempeture() {
  int data = analogRead(TEMP_SENSOR);
  float temp = 1023.0 / data - 1.0;
  temp = R0 * temp;
  temp = 1.0 / (log(temp / R0) / B + 1 / 298.15) - 273.15;
  Serial.write('2');
  Serial.print(String(temp));
}

void sendIR() {
  irSender.send(NEC, 0x61a0f00f, 20);
}

void setup() {
  Serial.begin(9600);
}

void loop() {
  while (Serial.available()) {
    char ack[1];
    Serial.readBytes(ack, 1);
    if (ack[0] == 'i') {
      sendIR();
    }
  }
  if (sendTemp > 10) {
    sendTempeture();
    sendTemp = 0;
  }
  sendTemp += 1;
  delay(500);
}
