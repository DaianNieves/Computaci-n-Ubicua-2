#include <SoftwareSerial.h>
#include <DHT.h>

SoftwareSerial picoSerial(2, 3); // RX=2, TX=3

const int LDR_PIN = A2;
const int LM35_PIN = A1;
const int MIC_PIN = A0;
#define DHTPIN 7
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  picoSerial.begin(9600);
  dht.begin();
  delay(2000);
}

void loop() {
  int ldr = analogRead(LDR_PIN);
  int lm35_raw = analogRead(LM35_PIN);
  float lm35_celsius = (lm35_raw * 5.0 * 100.0) / 1024.0; 

  int mic = analogRead(MIC_PIN);
  float hum = dht.readHumidity();
  float temp = dht.readTemperature(); // Temperatura del DHT11

  if (isnan(hum) || isnan(temp)) {
    Serial.println("Error sensor DHT");
    return;
  }

  String datos = String(ldr) + "," + String(lm35_celsius, 1) + "," + String(mic) + "," + String(hum) + "," + String(temp);

  picoSerial.println(datos);
  Serial.println("Enviando: " + datos);
  delay(5000);
}