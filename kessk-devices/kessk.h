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






#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266httpUpdate.h>
#include <ArduinoJson.h>
#include "aliyun_mqtt.h"
#include <WiFiUdp.h>
#include <airkiss.h>

#define CURRENT_VERSION 1
#define LED_PIN 2
#define DEFAULT_LAN_PORT  12476
#define LONG_CLICK_TIME 5000
#define RUNING_NORMAL 0
#define RUNING_NOWIFI 1
#define RUNING_NOMQTT 2
#define RUNING_CONFIG 3
#define RUNING_UPDATE 4
#define MSG_GETTING_SWTICH_STATUS   1
#define MSG_NORMAL_SWITCH_CONTROL   0
#define MSG_GET_DEVICE_VERSION      3
#define MSG_DEVICE_UPGRADE_REQUEST  6
#define MSG_DEVICE_UPGRADE_FAILED  7
#define PUSH_MESG_FORMAT "{\"type\":%d,\"version\": %d,\"status\":%d,\"device\":\"%s\",\"control_device\":\"%s\"}"
#define UPGRADE_URL "http://xxx.oss-cn-shenzhen.aliyuncs.com/kessk/switchDeviceUpdateVersion/kessk01/v%d/kessk_01_%s.bin"  // Device OTA upgrade path
#define TRY_UPGRADE_TIME 10000
#define CHECK_CONNECT_TIME 20000

class KessK
{
    /**
     * Device main controller class
     */
public:
    KessK();
    /**
     * Init the class, the values to connect to aliyun Iot. It will be run in Ardiuno setup() function.
     * s.1 : Check if a wifi connection.
     * s.2 : Check if MQTT connection.
     * s.3 : Set device runing mode is 0 or others. 0 for normal mode, 1 for no wifi connection, 2 for no MQTT connection, 3 for wifi configuration, 4 for device upgrade
     * @param productKey The device's product key
     * @param deviceName The deivce name in aliyun Iot
     * @param deviceSecret device secret
     */
	void init(String productKey,String deviceName, String deviceSecret);
	~KessK();

	/**
	 * The main loop function, it will be run in Arduino loop() function.
	 * s.1 : Check device runing mode.
	 * s.2 : For runing in normal mode,.
	 * s.2.1 : Check if control pin changes, turn on/off the replay. Push a switch status message to MQTT server.
	 * s.2.2 : Check if airkiss mode is activated.
	 * s.2.3 : Check if upgrade mode is activated.
	 * s.3 : For runing in airkiss mode.
	 * s.3.1 : Start Wechat airkiss, this will stop all wifi connection.
	 * s.3.2 : Start device discover while its connect to a wifi by airkiss.
	 * s.3.3 : Send data to the control device and then self restart.
	 * s.4 : For runing in upgrade mode.
	 * s.4.1 : Get the newer version number.
	 * s.4.2 : Goto ESP update.
	 */
	void loop();

	/**
	 * Control switch status by given value
	 * @param switchStatus True for turn on, other for turn off
	 */
	void controlSwitch(bool switchStatus);

	/**
	 * Turn on/off the switch
	 */
	void turnSwitch();

	/**
	 * Upgrade the device's sofware
	 * @param versionid The newer version number
	 */
	void updateDevice(unsigned int versionid);

	/**
	 * Start wechat airkiss configure
	 * @return success or faild
	 */
	bool startAirkiss();

	/**
	 * Start Wechat device discover and send data to the control deivce
	 */
	void startDiscover();

	bool checkWifiConnection();

	void switchButtonHaneller();

    String getMacAddress();
	void setLedPin(unsigned int pinid);
	void setControlPin(unsigned int pinid);
	void setReplayPin(unsigned int pinid);
	void setRegionId(String id);
	void setRuningMode(int mode);

protected:
    /**
     * Init aliyun client and connect to the server.
     * @return connect success or not.
     */
    bool initMQTTServer();

    /**
     * Check if connected to wifi.
     * @return
     */
    bool connectWiFi();

    /**
     * Push a message to aliyun MQTT server.
     * @param type
     */
    void pushMsg(int type,const char * controlDeviceName,bool reverse=false);

    /**
     * MQTT server subscribe callback function.
     * @param topic
     * @param payload
     * @param length
     */
    void handleMsg(char *topic, byte *payload, unsigned int length);

    void setGPIOMode();

    void longClick(unsigned long startTime);

    void stopWifiConfigure();

private:
	String _product_key, _device_name, _device_secret, _region_id="cn-shanghai";
	String _sub_topic, _update_topic, _device_mac_address, _device_prefix;
	unsigned int _led_pin=0, _control_pin=3, _replay_pin=0,_runing_mode=0;
  unsigned long _last_check_connect_time = 0;
	bool _switch_status;
	WiFiClient * _wifi_client;
    PubSubClient * _mqtt_client;
//	void * _mqtt_client;
    String DEVICE_TYPE = "gh_dc4ac7020883";
    String DEVICE_ID = "KessK_WifiModule_";
	
};
