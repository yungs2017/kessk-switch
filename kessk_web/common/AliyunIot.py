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

from aliyunsdkcore.client import AcsClient
from aliyunsdkiot.request.v20180120.CreateRuleActionRequest import CreateRuleActionRequest
from aliyunsdkiot.request.v20180120.CreateRuleRequest import CreateRuleRequest
from aliyunsdkiot.request.v20180120.DeleteRuleActionRequest import DeleteRuleActionRequest
from aliyunsdkiot.request.v20180120.GetDeviceStatusRequest import GetDeviceStatusRequest
from aliyunsdkiot.request.v20180120.RegisterDeviceRequest import RegisterDeviceRequest
from aliyunsdkiot.request.v20180120.StartRuleRequest import StartRuleRequest

from common.config import ALIYUN_ACCESS_KEY, ALIYUN_ACCESS_SECRET, ALIYUN_IOT_REGION, ALIYUN_IOT_CONTROL_APP_PRODUCT_KEY


class AliyunIot():
    """
    Handle Aliyun IoT
    """

    def __init__(self):
        """
        Init the Aliyun API client
        """
        self.client = AcsClient(ALIYUN_ACCESS_KEY, ALIYUN_ACCESS_SECRET, ALIYUN_IOT_REGION)

    def register_control_device(self,device_name=None):
        """
        Register a control device
        :param device_name: if no device name, Aliyun Iot will create one
        :return:
        """
        return self.register_device(product_key=ALIYUN_IOT_CONTROL_APP_PRODUCT_KEY,device_name=device_name)

    def register_device(self,product_key,device_name=None):
        """
        Register a device in Aliyun IoT
        :param product_key: Aliyun IoT product key, the deivce will register under this product
        :param device_name: optional
        :return:
        """
        request_aliyun = RegisterDeviceRequest()
        request_aliyun.set_accept_format('json')
        request_aliyun.set_ProductKey(product_key)
        if device_name is not None:
            request_aliyun.set_DeviceName(device_name)
        response = self.client.do_action_with_exception(request_aliyun)
        response = response.decode('utf8')
        response = json.loads(response)
        if response.get('Success'):
            return response['Data']
        return None

    def create_rule(self,rule_name,topic,product_key):
        """
        Create forwarding rules between Aliyun IoT devices
        :param rule_name: Must be the non-repeating name
        :param topic: Short topic in Aliyun API
        :param product_key: need for the API
        :return:
        """
        request = CreateRuleRequest()
        request.set_accept_format('json')
        request.set_Name(rule_name)
        request.set_ShortTopic(topic)
        request.set_ProductKey(product_key)
        request.set_DataType("JSON")
        request.set_TopicType("1")

        response = self.client.do_action_with_exception(request)
        response = response.decode('utf8')
        response = json.loads(response)
        print('Aliyun response is create rule ')
        print(response)
        if response["Success"]:
            return response
        return None

    def create_rule_action(self,rule_id,configuration):
        """
        The rule's action creation
        :param rule_id:
        :param configuration: example : "{\"topic\":\"/"+control_product_name+"/"+data['Data']['DeviceName']+"/user/get\",\"topicType\":1}"
        :return:
        """
        request = CreateRuleActionRequest()
        request.set_accept_format('json')
        request.set_Type("REPUBLISH")
        request.set_Configuration(configuration)
        request.set_RuleId(rule_id)
        response = self.client.do_action_with_exception(request)
        response = response.decode('utf8')
        response = json.loads(response)
        if response['Success']:
            return response
        return None

    def delete_rule_action(self,action_id):
        """
        Delete a rule action
        :param action_id:
        :return:
        """
        request = DeleteRuleActionRequest()
        request.set_accept_format('json')
        request.set_ActionId(action_id)
        response = self.client.do_action_with_exception(request)
        response = response.decode('utf8')
        response = json.loads(response)
        if response['Success']:
            return response
        return None


    def start_rule(self,rule_id):
        """
        Start the rule
        :param rule_id:
        :return:
        """
        request = StartRuleRequest()
        request.set_accept_format('json')

        request.set_RuleId(rule_id)

        response = self.client.do_action_with_exception(request)
        response = response.decode('utf8')
        response = json.loads(response)
        print("start rule is")
        print(response)
        if response["Success"]:
            return response
        return None

    def get_muti_device_status(self,device_binds):
        """
        Get devices status : online/ offline
        :param device_binds:
        :return:
        """
        request_aliyun = GetDeviceStatusRequest()
        request_aliyun.set_accept_format('json')
        for device in device_binds:
            request_aliyun.set_ProductKey(device.device.product_key)
            request_aliyun.set_DeviceName(device.device.device_name)
            response = self.client.do_action_with_exception(request_aliyun)
            response = response.decode('utf8')
            response = json.loads(response)
            if response["Success"]:
                if response["Data"]["Status"] == 'OFFLINE':
                    device.onActive = False

        return device_binds




