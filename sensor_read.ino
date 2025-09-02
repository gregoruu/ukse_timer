#include <PTE7300_I2C.h>

PTE7300_I2C mySensor;      // attach sensor
int16_t DSP_S;             // allocate memory for pressure register value

void setup() {
  // initiate serial communication
  Serial.begin(9600);
}

void loop() {
  // first check if the sensor is connected
  if (mySensor.isConnected()) {
    DSP_S = mySensor.readDSP_S();   // read pressure register value
    Serial.println(DSP_S);          // print value to serial bus
  }
  else {
    Serial.println("Device not connected");
  }

  delay(100);   // wait for 100ms
}
