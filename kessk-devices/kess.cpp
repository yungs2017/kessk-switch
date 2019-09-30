// The 3-Clause BSD License
// Copyright (C) 2019, KessK, all rights reserved.
// Copyright (C) 2019, Kison.Y, all rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
// following conditions are met:Redistribution and use in source and binary forms, with or without modification, are
// permitted provided that the following conditions are met:
// Redistributions of source code must retain the above copyright notice, this list of conditions and the following
// disclaimer.

// Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
// disclaimer in the documentation and/or other materials provided with the distribution.
// Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products
// derived from this software without specific prior written permission.

// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES,
// INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
// WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.





#include "kessk.h"

KessK::KessK() {
    this->_wifi_client = new WiFiClient();
    this->_mqtt_client = new PubSubClient(*this->_wifi_client);
    
}

void KessK::init(String productKey, String deviceName, String deviceSecret)
{
    this->_product_key = productKey;
    this->_device_name = deviceName;
    this->_device_secret = deviceSecret;
    DEVICE_ID = DEVICE_ID + WiFi.softAPmacAddress().c_str();
    if (this->_control_pin == 3 || this->_replay_pin == 3){
      pinMode(3, FUNCTION_3);
    }
    if (this->_control_pin == 1 || this->_replay_pin == 1){
      pinMode(1, FUNCTION_3);
    }
    this->_sub_topic = "/" +  productKey +  "/" +  deviceName + "/user/get";
    this->_update_topic = "/" +  productKey + "/" + deviceName +  "/user/update";
    WiFi.mode(WIFI_STA);
    this->setGPIOMode();
//    this->_mqtt_client->setCallback(this->handleMsg);
    this->_mqtt_client->setCallback([this] (char* topic, byte* payload, unsigned int length) { this->handleMsg(topic, payload, length); });
    if (checkWifiConnection()){
         this->_runing_mode = 0;
    }


}

void KessK::setGPIOMode() {
    pinMode(this->_replay_pin, OUTPUT);
    pinMode(this->_control_pin, INPUT);
    digitalWrite(this->_replay_pin, LOW); // make GPIO0 output low
    this->_switch_status = false;
}

bool KessK::startAirkiss() {
    Serial.println("start airkiss...");
    WiFi.mode(WIFI_STA);
    WiFi.beginSmartConfig();
    bool LIGHT = HIGH;
    while (1) {
        if (this->_runing_mode != RUNING_CONFIG){
            this->stopWifiConfigure();
            return false;
        }
        this->turnSwitch();
        //Serial.println("................................................................");
//        digitalWrite(2, LIGHT);
        if (WiFi.smartConfigDone()) {
            Serial.println("");
            Serial.println("airkiss Success");
            Serial.printf("SSID:%s\r\nPSW:%s\r\n", WiFi.SSID().c_str(), WiFi.psk().c_str());
            WiFi.setAutoConnect(true);
            break;
        }
        if (LIGHT == LOW) {
            LIGHT = HIGH;
        } else {
            LIGHT = LOW;
        }
        this->switchButtonHaneller();
        delay(800);
    }
//    digitalWrite(2, HIGH);
    if (this->_runing_mode == RUNING_CONFIG) {
        startDiscover();
        this->checkWifiConnection();
    }
    return true;
}

void KessK::startDiscover() {
    WiFiUDP udp;
    udp.begin(DEFAULT_LAN_PORT);
    char udpPacket[255];
    uint8_t lan_buf[255];
    uint16_t lan_buf_len;

    const airkiss_config_t airkissConf = {
            (airkiss_memset_fn)&memset,
            (airkiss_memcpy_fn)&memcpy,
            (airkiss_memcmp_fn)&memcmp,
            0
    };

    while (1) {
        if (this->_runing_mode != RUNING_CONFIG) {
            this->stopWifiConfigure();
            return;
        }
        this->switchButtonHaneller();
        int packetSize = udp.parsePacket();
        if (packetSize) {
            Serial.printf("Received %d bytes from %s, port %d\r\n", packetSize, udp.remoteIP().toString().c_str(), udp.remotePort());
            int len = udp.read(udpPacket, 255);
            if (len > 0) {
                udpPacket[len] = 0;
            }
            Serial.printf("UDP packet contents: %2x\r\n", udpPacket);
            Serial.println(udpPacket);
            int ret = airkiss_lan_recv(udpPacket, len, &airkissConf);
            int packret;
            switch (ret) {
                //接收到发现设备请求数据包
                case AIRKISS_LAN_SSDP_REQ:
                    Serial.println("--->>> find device");
                    Serial.println(DEVICE_TYPE);
                    Serial.println(DEVICE_ID);
                    lan_buf_len = sizeof(lan_buf);
                    //打包数据
                    packret = airkiss_lan_pack(AIRKISS_LAN_SSDP_RESP_CMD, (char *)DEVICE_TYPE.c_str(), (char *)DEVICE_ID.c_str(), 0, 0, lan_buf, &lan_buf_len, &airkissConf);
                    if (packret != AIRKISS_LAN_PAKE_READY) {
                        Serial.println("pack lan packet error");
                        return;
                    }
                    Serial.printf("udp pack is %2x,length is %d\r\n", lan_buf, sizeof(lan_buf));
                    udp.beginPacket(udp.remoteIP(), udp.remotePort());
                    Serial.println(udp.write(lan_buf, sizeof(lan_buf)));
                    udp.endPacket();
                    return;
                    break;
                default:
                    Serial.println("pack is not ssdq req");
                    break;
            }
        }
    }
}


void KessK::loop() {
    this->switchButtonHaneller();
    this->_mqtt_client->loop();
    if (millis() - this->_last_check_connect_time > CHECK_CONNECT_TIME && this->_runing_mode == RUNING_NOWIFI){
      Serial.println("Runing mode is : ");
      Serial.println(this->_runing_mode);
      checkWifiConnection();
    }
    delay(5);
}



void KessK::longClick(unsigned long startTime) {
    while (1) {
        if (digitalRead(this->_control_pin) == LOW)
            return;
        if (millis() - startTime >= LONG_CLICK_TIME){
            Serial.println("Long Click Now");
            if (this->_runing_mode == RUNING_NORMAL || this->_runing_mode == RUNING_NOWIFI || this->_runing_mode == RUNING_NOMQTT){
                this->_runing_mode = RUNING_CONFIG;
                this->startAirkiss();
                return;
            }
            else if (this->_runing_mode == RUNING_CONFIG){
                Serial.println("Stop smart config manually");
                this->_runing_mode = RUNING_NORMAL;
                return;
            }

        }
        delay(10);
    }
}

void KessK::stopWifiConfigure() {
    WiFi.stopSmartConfig();
    WiFi.mode(WIFI_STA);
    this->checkWifiConnection();
}

void KessK::switchButtonHaneller() {
    bool controlPinStatus = (digitalRead(this->_control_pin) == HIGH);
    if (controlPinStatus) {
        unsigned long lastMs = millis();
        Serial.print("Now Control switch status is :");
            Serial.print(this->_switch_status);
            Serial.println("");
        this->turnSwitch();
        this->longClick(lastMs);
    }
}

bool KessK::checkWifiConnection() {
    WiFi.begin();
    int count = 0;
    this->_last_check_connect_time = millis();
    while ( count < 150 ) {
        if (WiFi.status() == WL_CONNECTED) {
//            Serial.println();
            Serial.println("Connected!");
            if (initMQTTServer())
                this->_runing_mode = RUNING_NORMAL;
            return (true);
        }
        this->switchButtonHaneller();
        delay(50);
//        Serial.print(".");
        count++;
    }
    this->_runing_mode = RUNING_NOWIFI;
    Serial.println("Timed out.");
    return false;
}

bool KessK::connectWiFi() {}

void KessK::controlSwitch(bool switchStatus) {
   if (switchStatus != this->_switch_status)
        this->turnSwitch();  
}

String KessK::getMacAddress() {}

void KessK::handleMsg(char *topic, byte *payload, unsigned int length) {
     StaticJsonDocument<200> jsonMsg;
    deserializeJson(jsonMsg, (char *)payload);

Serial.println("Message arrived ");
Serial.println(serializeJson(jsonMsg, Serial));
Serial.println("Message finish ");
    
    const int type = jsonMsg["type"];
    int statusMsg = jsonMsg["status"];
    const char* controlDeviceName = jsonMsg["control_device"];
    switch (type) {
        case MSG_GETTING_SWTICH_STATUS:
            this->pushMsg(MSG_NORMAL_SWITCH_CONTROL,controlDeviceName);
            break;
        case MSG_NORMAL_SWITCH_CONTROL:
            Serial.print("Now switch status is :");
            Serial.print(this->_switch_status);
            Serial.println("");
            this->controlSwitch(statusMsg);
//            this->pushMsg(MSG_NORMAL_SWITCH_CONTROL,controlDeviceName);
            break;
        case MSG_GET_DEVICE_VERSION:
            this->pushMsg(MSG_GET_DEVICE_VERSION,controlDeviceName);
            break;
        case MSG_DEVICE_UPGRADE_REQUEST:
            if (statusMsg > CURRENT_VERSION)
                Serial.print("The newer version is : ");
                Serial.print(statusMsg);
                Serial.println("Start to Upgrade the device system");
                delay(3000);
                this->updateDevice(statusMsg);
            this->pushMsg(MSG_DEVICE_UPGRADE_REQUEST,controlDeviceName);
            break;
    }

    
}

bool KessK::initMQTTServer() {
//    if (this->_runing_mode != RUNING_NORMAL)
//        return false;
    if (!this->_mqtt_client->connected()){
        // Length (with one extra character for the null terminator)
//        int str_len = str.length() + 1;
        char productKeyChar[_product_key.length() + 1];
        char deviceNameChar[_device_name.length() + 1];
        char deviceSecretChar[_device_secret.length() + 1];
        _product_key.toCharArray(productKeyChar, _product_key.length() + 1);
        _device_name.toCharArray(deviceNameChar, _device_name.length() + 1);
        _device_secret.toCharArray(deviceSecretChar, _device_secret.length() + 1);
        if (connectAliyunMQTT(*this->_mqtt_client, productKeyChar, deviceNameChar, deviceSecretChar)) {
            Serial.println("Connected to aliyun Iot MQTT server");
            char subTopicChar[_sub_topic.length() + 1];
            _sub_topic.toCharArray(subTopicChar, _sub_topic.length() + 1);
            this->_mqtt_client->subscribe(subTopicChar);
            pushMsg(MSG_NORMAL_SWITCH_CONTROL,(char *)this->_device_name.c_str());
            return true;
        }
        this->_runing_mode = RUNING_NOMQTT;
        return false;
    }
//    this->_runing_mode = RUNING_NOMQTT;
    return true;
}

void KessK::pushMsg(int type,const char * controlDeviceName,bool reverse) {
    char jsonBuf[200];
    if (reverse)
      sprintf(jsonBuf,PUSH_MESG_FORMAT, type,CURRENT_VERSION,!this->_switch_status,(char *)this->_device_name.c_str(),controlDeviceName);
    else
      sprintf(jsonBuf,PUSH_MESG_FORMAT, type,CURRENT_VERSION,this->_switch_status,(char *)this->_device_name.c_str(),controlDeviceName);
//    Serial.println(jsonBuf);
    this->_mqtt_client->publish((char *)this->_update_topic.c_str(), jsonBuf);
    return;
}

void KessK::setControlPin(unsigned int pinid) {}

void KessK::setLedPin(unsigned int pinid) {}

void KessK::setRegionId(String id) {}

void KessK::setReplayPin(unsigned int pinid) {}

void KessK::setRuningMode(int mode) {}

void KessK::turnSwitch() {
    if (this->_switch_status){
        this->_switch_status = false;
        digitalWrite(this->_replay_pin, LOW);
    }

    else{
        this->_switch_status = true;
        digitalWrite(this->_replay_pin, HIGH);
    }

    
    
    if (this->_runing_mode == RUNING_NORMAL){
      Serial.print("Now RUNGING MODE is :");
            Serial.print(this->_runing_mode);
            Serial.println((char *)this->_update_topic.c_str());
        pushMsg(MSG_NORMAL_SWITCH_CONTROL,(char *)this->_device_name.c_str());
    }
        
}

void KessK::updateDevice(unsigned int versionid) {
    char url[200];
    String address = WiFi.softAPmacAddress();
    address.replace(":","");
    sprintf(url,UPGRADE_URL,versionid,address.c_str());
    Serial.println(url);
    unsigned long lastMs = millis();
    while(millis() - lastMs <= TRY_UPGRADE_TIME){
      ESPhttpUpdate.setLedPin(LED_BUILTIN, HIGH);
      ESPhttpUpdate.rebootOnUpdate(false);
      t_httpUpdate_return ret = ESPhttpUpdate.update(*this->_wifi_client, url);
      switch (ret) {
        case HTTP_UPDATE_FAILED:
          Serial.printf("HTTP_UPDATE_FAILD Error (%d): %s\n", ESPhttpUpdate.getLastError(), ESPhttpUpdate.getLastErrorString().c_str());
          break;
  
        case HTTP_UPDATE_NO_UPDATES:
          Serial.println("HTTP_UPDATE_NO_UPDATES");
          break;
  
        case HTTP_UPDATE_OK:
          Serial.println("HTTP_UPDATE_OK");
          delay(500);
          Serial.println("Reset..");
          ESP.restart();
          break;
      }
      delay(500);
    }

    // Update failure
    if (checkWifiConnection()){
      this->_runing_mode = RUNING_NORMAL;
      pushMsg(MSG_DEVICE_UPGRADE_FAILED,(char *)this->_device_name.c_str());
    }
      
}

KessK::~KessK() {}
