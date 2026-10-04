#include <Wire.h>

#define MPU_ADDR 0x68
#define SDA_PIN 21
#define SCL_PIN 22
#define PIEZO_PIN 34

const unsigned long SAMPLE_INTERVAL_MS = 10;
const unsigned long RECORDING_TIME_MS = 3000;

// MPU6050 registers
#define PWR_MGMT_1   0x6B
#define ACCEL_XOUT_H 0x3B

void writeMPU(byte reg, byte data) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  Wire.write(data);
  Wire.endTransmission();
}

int16_t read16() {
  int16_t value = Wire.read() << 8 | Wire.read();
  return value;
}

void readMPU(
  int16_t &ax,
  int16_t &ay,
  int16_t &az,
  int16_t &gx,
  int16_t &gy,
  int16_t &gz
) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(ACCEL_XOUT_H);
  Wire.endTransmission(false);

  Wire.requestFrom(MPU_ADDR, 14, true);

  ax = read16();
  ay = read16();
  az = read16();

  // Temperature — ignore
  read16();

  gx = read16();
  gy = read16();
  gz = read16();
}

bool testMPU() {
  Wire.beginTransmission(MPU_ADDR);
  return Wire.endTransmission() == 0;
}

void setup() {
  Serial.begin(115200);

  Wire.begin(SDA_PIN, SCL_PIN);

  // Wake MPU6050 from sleep
  writeMPU(PWR_MGMT_1, 0x00);

  delay(100);

  if (!testMPU()) {
    Serial.println("ERROR: MPU6050 not found at 0x68");
    while (1);
  }

  analogReadResolution(12);

  Serial.println("ESP32_READY");
}

void recordSample() {

  unsigned long startTime = millis();
  unsigned long nextSample = startTime;

  Serial.println("RECORDING_START");
  Serial.println("time,ax,ay,az,gx,gy,gz,piezo");

  while (millis() - startTime < RECORDING_TIME_MS) {

    if (millis() >= nextSample) {

      int16_t axRaw, ayRaw, azRaw;
      int16_t gxRaw, gyRaw, gzRaw;

      readMPU(
        axRaw,
        ayRaw,
        azRaw,
        gxRaw,
        gyRaw,
        gzRaw
      );

      // Convert to the same units used in your dataset
      float ax = axRaw / 16384.0;
      float ay = ayRaw / 16384.0;
      float az = azRaw / 16384.0;

      float gx = gxRaw / 131.0;
      float gy = gyRaw / 131.0;
      float gz = gzRaw / 131.0;

      int piezo = analogRead(PIEZO_PIN);

      unsigned long t = millis() - startTime;

      Serial.print(t);
      Serial.print(",");

      Serial.print(ax, 4);
      Serial.print(",");

      Serial.print(ay, 4);
      Serial.print(",");

      Serial.print(az, 4);
      Serial.print(",");

      Serial.print(gx, 4);
      Serial.print(",");

      Serial.print(gy, 4);
      Serial.print(",");

      Serial.print(gz, 4);
      Serial.print(",");

      Serial.println(piezo);

      nextSample += SAMPLE_INTERVAL_MS;
    }
  }

  Serial.println("RECORDING_END");
  Serial.println("READY");
}

void loop() {

  if (Serial.available()) {

    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "START") {
      recordSample();
    }
  }
}
