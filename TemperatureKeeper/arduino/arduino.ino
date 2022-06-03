// TemperatureKeeper - TemperatureSensor
#include "DHT.h"

#define DHT_PIN 4
#define DHTTYPE DHT11
#define THRESHOLD_CONTROL_PIN A0
#define THRESHOLD_MIN 10
#define THRESHOLD_MAX 40
#define THRESHOLD_CONTROL_MIN 0
#define THRESHOLD_CONTROL_MAX 1023

DHT dht(DHT_PIN, DHTTYPE);

int triggerTemp = THRESHOLD_CONTROL_MIN;
int sendTemp = 0;

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
  Serial.flush();
}

void sendTempHumd() {
  float t = dht.readTemperature();
  if (isnan(t)) {
    return;
  }
  Serial.write('2');
  Serial.print(String(t));
  waitAck();
}

void sendThreshold() {
  triggerTemp = map(analogRead(THRESHOLD_CONTROL_PIN),
                    THRESHOLD_CONTROL_MIN,
                    THRESHOLD_CONTROL_MAX,
                    THRESHOLD_MIN,
                    THRESHOLD_MAX);
  Serial.write('1');
  Serial.write(triggerTemp);
  waitAck();
}

void setup() {
  Serial.begin(9600);
  dht.begin();
  sendTempHumd();
  sendThreshold();
}

void loop() {
  sendThreshold();
  if (sendTemp > 10) {
    sendTempHumd();
    sendTemp = 0;
  }
  sendTemp += 1;
  delay(500);
}
