# The 3-Clause BSD License
# Copyright (C) 2019, KessK, all rights reserved.
# Copyright (C) 2019, Kison.Y, all rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following
# disclaimer.

# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with the distribution.
# Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products
# derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import json
import time

from aliyun_client import Aliyun


class VirtualDevice(Aliyun):

    def __init__(self,product_key,device_name,device_secret):
        Aliyun.__init__(self, product_key=product_key,
                        device_name=device_name,
                        device_secret=device_secret)
        self.connect()
        self.name = "Client ESP8266"
        self._status = True
        self._version = 1
        self._msg = "{\"type\":%d,\"version\": %d,\"status\":%d,\"device\":\"%s\",\"control_device\":\"%s\"}"


    def loop(self):
        while True:
            swith_status = input("Please input on/off\r\n")
            swith_status = swith_status.upper()
            if swith_status == "ON":
                print("Turnning on...")
                self._status = False
                self._turnSwitch()
            elif swith_status == "OFF":
                self._status = True
                self._turnSwitch()
            continue

    def on_topic_message(self,topic, payload, qos, userdata):
        print('Message arrival')
        json_string = json.loads(payload.decode('utf8'))
        if json_string["type"] == 1:
            print('Push status to control apps')
            self._pushStatusMsg(json_string["control_device"])
        elif json_string["type"] == 3:
            print("Push device version number")
            self._pushDeviceVersion(json_string["control_device"])
        elif json_string["type"] == 6:
            print("Begin upgrade...")
            # Begin upgrade
            time.sleep(10)
            self._pushStatusMsg(json_string["control_device"])
        else:
            if json_string["status"] is not self._status:
                self._turnSwitch()


    def _pushStatusMsg(self,control_device):
        msg = self._msg % (0,self._version,self._status,self._deviceName,control_device)
        self.push_message(msg)

    def _pushDeviceVersion(self,control_device):
        msg = self._msg % (3, self._version, self._status, self._deviceName, control_device)
        self.push_message(msg)

    def _pushUpdateFiled(self,control_device):
        msg = self._msg % (7, self._version, self._status, self._deviceName, control_device)
        self.push_message(msg)

    def _turnSwitch(self,control_device=""):
        self._status = not self._status
        self._pushStatusMsg(control_device)
        if self._status:
            print("Turn ON")
        else:
            print("Turn OFF")



if __name__ == "__main__":
    device = VirtualDevice(product_key='your ESP8266 device product key',
                 device_name='device name',
                 device_secret='device secret')
    device.loop()