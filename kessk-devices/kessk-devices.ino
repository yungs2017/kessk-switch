#include "kessk.h"

const String PRODUCT_KEY = "yours Aliyun IoT product key";
const String DEVICE_NAME = "Aliyun IoT device name";
const String DEVICE_SECRET = "Aliyun IoT device secret";

KessK kessk;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  kessk.init(PRODUCT_KEY,DEVICE_NAME,DEVICE_SECRET);

}

void loop() {
  // put your main code here, to run repeatedly:
  kessk.loop();
}
