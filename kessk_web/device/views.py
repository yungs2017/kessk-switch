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



import datetime
import hashlib
import random
import string
import time

from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view

from common.AliyunIot import AliyunIot
from common.ExceptionAPI import AValidation400Error, response_json
from common.WechatCommonView import WechatCommonView
from common.config import ErrorCodes, DEVICE_MASK, DEVICE_NAME_DEFAULT, ALIYUN_IOT_CONTROL_APP_PRODUCT_KEY
from device.models import Device, DeviceBind, ControlDevice, AliyunIotRules
from device.wexinSignature import Signature
from rest_framework import status, generics


class BindView(WechatCommonView):
    """
    Configure the device to connect to wifi AP in Wechat client
    """

    template_name = "config-wechat-wifi.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sign = Signature(self.full_url)
        sign.sign()
        print(sign.ret['nonceStr'])
        print(sign.ret['jsapi_ticket'])
        print(sign.ret['timestamp'])
        print(sign.ret['url'])
        context['sign'] = sign
        return context

#
# class BindDeviceAPI(generics.CreateAPIView):
#
#     def post(self, request, *args, **kwargs):
#         print("ok")

@api_view(['POST'])
def bindDevice(request):
    if not check_login(request):
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['not_allowed'],
                                  errcode=ErrorCodes['global']['not_allowed'])
    chip_id = request.POST.get('chip')
    if not request.session.get('userid') or not chip_id:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['required'],
                                  errcode=ErrorCodes['global']['required'])

    chip_id = str(chip_id).replace(DEVICE_MASK, '')
    chip_id = str(chip_id).replace(':', '')

    try:
        device = Device.objects.get(device_chipid=chip_id)
        user = User.objects.get(id=request.session['userid'])
    except Device.DoesNotExist:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['device']['not_exits'],
                                  errcode=ErrorCodes['device']['not_exits'])
    except User.DoesNotExist:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['user']['not_exits'],
                                  errcode=ErrorCodes['user']['not_exits'])

    device_action = DeviceBindAction(device=device,user=user)
    device_action.unbinding_device()
    device_bind = device_action.bind_device()


    return JsonResponse(response_json(data={'device_name':device_bind.device_name,'id':device_bind.id}), status=status.HTTP_201_CREATED)

@api_view(['POST'])
def bindShareDevice(request):
    if not check_login(request):
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['not_allowed'],
                                  errcode=ErrorCodes['global']['not_allowed'])
    share_code = request.POST.get('share_code')
    if not request.session.get('userid') or not share_code:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['required'],
                                  errcode=ErrorCodes['global']['required'])
    share_info = cache.get(share_code)
    if share_info is None:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['device']['share_oft'],
                                  errcode=ErrorCodes['device']['share_oft'])
    user_id = share_info.get("user")
    device_id = share_info.get("device")

    try:
        user = User.objects.get(id=user_id)
        device = Device.objects.get(id=device_id)
        current_user = User.objects.get(id=request.session.get('userid'))
        device_bind = DeviceBind.objects.get(user=user, device=device, onActive=True)
    except User.DoesNotExist or Device.DoesNotExist or DeviceBind.DoesNotExist:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['not_allowed'],
                                  errcode=ErrorCodes['global']['not_allowed'])
    device_action = DeviceBindAction(device=device, user=current_user)
    device_bind = device_action.bind_device(origin_user=user)
    return JsonResponse(response_json(data={'device_name': device_bind.device_name, 'id': device_bind.id}),
                        status=status.HTTP_201_CREATED)





@api_view(['PUT'])
def ccnameDevice(request):
    if not check_login(request):
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['not_allowed'],
                                  errcode=ErrorCodes['global']['not_allowed'])
    chip_id = request.POST.get('chip')
    name = request.POST.get('name')
    is_name = request.POST.get('is_name')
    if not chip_id:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['required'],
                                  errcode=ErrorCodes['global']['required'])

    device_bind_action = DeviceBindAction(device=None,user=User.objects.get(id=request.session.get('userid')))
    if not is_name:
        device_bind = device_bind_action.update_device_name(device_bind_id=chip_id,name=name)
    else:
        device_bind = device_bind_action.update_device_name(device_bind_id=DeviceBind.objects.get(device__device_name=chip_id,user__id=request.session.get('userid'),onActive=True).id, name=name)
    return JsonResponse(response_json(data={}),
                        status=status.HTTP_201_CREATED)



class DeviceBindAction():

    def __init__(self,device,user):
        self.device = device
        self.user = user
        self._deviceRule = DeviceRule(self.device,None)
        control_device = self._deviceRule.create_control_device(self.user)
        self._deviceRule.control_device = control_device



    def unbinding_device(self):
        self._deviceRule.delete_device_all_action()
        try:
            bind_log = DeviceBind.objects.filter(device=self.device, onActive=True).exclude(user=self.user)
            bind_log.update(onActive=False, unbind_time=datetime.datetime.now())
            bind_log = DeviceBind.objects.filter(device=self.device,onActive=True,origin_user__isnull=False).exclude(origin_user=self.user)
            bind_log.update(onActive=False, unbind_time=datetime.datetime.now())
        except DeviceBind.DoesNotExist:
            pass

    def unbind_user_device(self):
        try:
            if DeviceBind.objects.filter(device=self.device, user=self.user,onActive=True,origin_user=None).exists():
                # Current user is the main user
                self._deviceRule.delete_share_rule_action()
                bind_log = DeviceBind.objects.filter(device=self.device, onActive=True, origin_user=self.user)
                bind_log.update(onActive=False, unbind_time=datetime.datetime.now())
            bind_log = DeviceBind.objects.filter(device=self.device, user=self.user, onActive=True)
            bind_log.update(onActive=False, unbind_time=datetime.datetime.now())
            # Delete rule action
            self._deviceRule.delete_device2control_action()
            # self._deviceRule.delete_control2device_action()
        except DeviceBind.DoesNotExist:
            pass

    def get_user_device_name(self):
        user_devices_count = DeviceBind.objects.filter(user=self.user, onActive=True).count() + 1
        device_name = DEVICE_NAME_DEFAULT + str(user_devices_count)
        return device_name

    def bind_device(self,device_name=None,origin_user=None):
        """
        Binding steps:
        Step1. Create if not exists a binding log.
        Step2. Create if not exists a device's rule.
        Step3. Create if not exists a control device's rule  # No more used
        Step4. Create if there is no rule action from device to control device.
        Step5. Create if there is no rule action from control device to device. # No more used
        Step6. Create if there is no rule action from current control device to share's control device # No more used
        Step7. Create if there is no rule action from share's control device to current control device # No more used
        :param device_name:
        :return:
        """
        # Step.1
        if not DeviceBind.objects.filter(user=self.user, device=self.device,onActive=True).exists():
            if device_name is None:
                device_name = self.get_user_device_name()
            device_bind = DeviceBind(
                device=self.device,
                user=self.user,
                origin_user=origin_user,
                device_name=device_name,
                onActive=True,
            )
            device_bind.save()

        # Step.2-5
        self._deviceRule.create_device2control_action()
        # self._deviceRule.create_control2device_action()


        #Step.6-7
        # if origin_user is not None:
        #     origin_user_control = self._deviceRule.create_control_device(origin_user)
        #     self._deviceRule.create_share_rule_action(origin_user_control)
        return DeviceBind.objects.get(user=self.user, device=self.device,onActive=True)

    def update_device_name(self,device_bind_id,name):
        try:
            device_bind = DeviceBind.objects.get(id=device_bind_id)
        except DeviceBind.DoesNotExist:
            raise AValidation400Error(detail="Unknow", code=ErrorCodes['device']['not_exits'],
                                      errcode=ErrorCodes['device']['not_exits'])
        if not device_bind.user.id == self.user.id:
            raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['not_allowed'],
                                      errcode=ErrorCodes['global']['not_allowed'])
        if name is None or name == device_bind.device_name:
            pass
        else:
            device_bind.device_name = name
            device_bind.save(update_fields=['device_name'])
        return device_bind


class ControlDeviceAction():

    def __init__(self,user):
        self.user = user
        self._aliyun =  AliyunIot()



    def create_control_device(self):
        """
        Create a control device when it dose not exists.
        Each user has only one control device
        :return:
        """
        if not ControlDevice.objects.filter(user=self.user).exists():
            response = self._aliyun.register_control_device()
            print('Aliyun response is ')
            print(response)
            if response is not None:
                control_device = ControlDevice(
                    user=self.user,
                    product_name='KessK_Controllor',
                    device_name=response['DeviceName'],
                    product_key=response['ProductKey'],
                    device_secret=response['DeviceSecret'],
                )
                control_device.save()
        return ControlDevice.objects.get(user=self.user)

    def create_device2control_rule(self,device_bind,rule_name=None):
        """
        Create Aliyun IoT rule from the esp8266 device to the control device.
        It will only be created once.
        :param device_bind:
        :param rule_name:
        :return:
        """
        if rule_name is None:
            rule_name = device_bind.device.device_name + "_2control_rule"
        topic = "/"+device_bind.device.device_name+"/user/update"
        if not AliyunIotRules.objects.filter(short_topic=topic,bind_device=device_bind).exists():
            data = self._aliyun.create_rule(rule_name=rule_name,topic=topic,product_key=device_bind.device.product_key)
            if data is not None:
                aliyun_iot_relu = AliyunIotRules(
                    name=device_bind.device.device_name + self.user.first_name,
                    short_topic=topic,
                    ruleid=data["RuleId"],
                    bind_device=device_bind,
                    requestid=data["RequestId"]
                )
                aliyun_iot_relu.save()
                data["rule_name"] = rule_name

        return AliyunIotRules.objects.get(short_topic=topic,bind_device=device_bind)

    def create_control2device_rule(self,device_bind,rule_name=None):
        if rule_name is None:
            rule_name = self.user.first_name + str(time.time()).replace('.','')


    def create_device2control_rule_action(self,relu_id,rule_name,configuration,device_bind):
        if not AliyunIotRules.objects.filter(ruleid=relu_id,action_config=configuration).exists():
            data = self._aliyun.create_rule_action(relu_id,configuration)
            if data is not None:
                aliyun_iot_relu_ = AliyunIotRules(
                    name=rule_name + '_action_',
                    ruleid=relu_id,
                    bind_device=device_bind,
                    requestid=data["RequestId"],
                    action_type="REPUBLISH",
                    action_config=configuration,
                )
                aliyun_iot_relu_.save()
        return AliyunIotRules.objects.get(ruleid=relu_id,action_config=configuration)

    def start_rule(self,rule_id):
        self._aliyun.start_rule(rule_id)


class DeviceRule():

    def __init__(self,device,control_device):
        self.device = device
        self.control_device = control_device
        self._aliyun = AliyunIot()

    def create_control_device(self,user):
        """
        Create a control device when it dose not exists.
        Each user has only one control device
        :return:
        """
        if not ControlDevice.objects.filter(user=user).exists():
            response = self._aliyun.register_control_device()
            print('Aliyun response is ')
            print(response)
            if response is not None:
                control_device = ControlDevice(
                    user=user,
                    product_name='KessK_Controllor',
                    device_name=response['DeviceName'],
                    product_key=response['ProductKey'],
                    device_secret=response['DeviceSecret'],
                )
                control_device.save()
        return ControlDevice.objects.get(user=user)


    def create_share_rule_action(self,origin_user_control):
        # Get control device rule
        control_device_rule = self.create_control_rule()
        # Get share's control device rule
        share_control_device_rule = self.create_rule(origin_user_control.device_name + "_2device_rule",
                                                     "/" + origin_user_control.device_name + "/user/update",
                                                     origin_user_control.product_key, origin_user_control.id, True)
        # Create control device to share's control device action
        configuration = "{\"topic\":\"/" + self.control_device.product_key + "/" + self.control_device.device_name + "/user/get\",\"topicType\":1}"
        self.create_rule_action(share_control_device_rule.ruleid, configuration, self.control_device.id, True)
        # Create share's control device to current control device
        configuration = "{\"topic\":\"/" + origin_user_control.product_key + "/" + origin_user_control.device_name + "/user/get\",\"topicType\":1}"
        self.create_rule_action(control_device_rule.ruleid, configuration, origin_user_control.id, True)

    def delete_share_rule_action(self):
        # Get all user share devices
        all_share_bind_log = DeviceBind.objects.filter(device=self.device,origin_user=self.control_device.user,onActive=True)
        control_device_rule = AliyunIotRules.objects.get(isControlDevice=True,device_id=self.control_device.id,isAction=False)
        for share_bind_log in all_share_bind_log:
            current_control_device = self.create_control_device(share_bind_log.user)
            current_rule = AliyunIotRules.objects.get(isControlDevice=True,device_id=current_control_device.id,isAction=False)
            try:
                share_to_control_action = AliyunIotRules.objects.get(isAction=True,isControlDevice=True,
                                                                     ruleid=control_device_rule.ruleid,
                                                                     device_id=current_control_device.id)
                self._aliyun.delete_rule_action(share_to_control_action.action_id)
                share_to_control_action.delete()
            except AliyunIotRules.DoesNotExist:
                continue

            try:
                control_to_share_action = AliyunIotRules.objects.get(isAction=True, isControlDevice=True,
                                                                     ruleid=current_rule.ruleid,
                                                                     device_id=self.control_device.id)
                self._aliyun.delete_rule_action(control_to_share_action.action_id)
                control_to_share_action.delete()
            except AliyunIotRules.DoesNotExist:
                continue

    def delete_device_all_action(self):
        # Step.1 Delete device all actions. These rule action is from control devices to the esp8266 device
        all_device_action = AliyunIotRules.objects.filter(isAction=True,isControlDevice=False,device_id=self.device.id)
        for action in all_device_action:
            self._aliyun.delete_rule_action(action.action_id)
            action.delete()
        # Step2. Delete all control devices actions. These rule action is from the esp8266 to control device
        try:
            device_rule = AliyunIotRules.objects.get(isAction=False,isControlDevice=False,device_id=self.device.id)
            all_device_action = AliyunIotRules.objects.filter(ruleid=device_rule.ruleid,isAction=True)
            for action in all_device_action:
                self._aliyun.delete_rule_action(action.action_id)
                action.delete()
        except AliyunIotRules.DoesNotExist:
            pass


    def create_device_rule(self):
        """
        Create Aliyun IoT rule from the esp8266 device to the control devices.
        It will only be created once.
        :return: The device's rule
        """
        name = self.__md5(self.device.device_name + "_2control_rule")
        topic = self.device.device_name + "/user/update"
        return self.create_rule(name,topic,self.device.product_key,self.device.id,False)

    def create_control_rule(self):
        """
        Create Aliyun IoT rule from the control device device to the esp8266 devices.
        It will only be created once.
        :return: The device's rule
        """
        name = self.__md5(self.control_device.device_name + "_2device_rule")
        topic = "/" + self.control_device.device_name + "/user/update"
        return self.create_rule(name,topic,self.control_device.product_key,self.control_device.id,True)

    def create_device2control_action(self):
        """
        Create action from esp8266 to control device
        :return: The action object
        """
        device_rule = self.create_device_rule()
        configuration = "{\"topic\":\"/" + self.control_device.product_key + "/" + self.control_device.device_name + "/user/get\",\"topicType\":1}"
        action = self.create_rule_action(device_rule.ruleid,configuration,self.control_device.id,True)
        self._aliyun.start_rule(device_rule.ruleid)
        return action

    def create_control2device_action(self):
        """
        Create action from control deivce to esp8266
        :return: The action object
        """
        device_rule = self.create_control_rule()
        configuration = "{\"topic\":\"/" + self.device.product_key + "/" + self.device.device_name + "/user/get\",\"topicType\":1}"
        action = self.create_rule_action(device_rule.ruleid, configuration, self.device.id, False)
        self._aliyun.start_rule(device_rule.ruleid)
        return action

    def delete_device2control_action(self):
        """
        Delete rule action from esp8266 to control device
        :return:
        """
        device_rule = self.create_device_rule()
        try:
            device_action = AliyunIotRules.objects.get(ruleid=device_rule.ruleid,isAction=True,device_id=self.control_device.id,isControlDevice=True)
        except AliyunIotRules.DoesNotExist:
            return
        self._aliyun.delete_rule_action(device_action.action_id)
        device_action.delete()

    def delete_control2device_action(self):
        """
        Delete rule action from control device to esp8266
        :return:
        """
        device_rule = self.create_control_rule()
        try:
            device_action = AliyunIotRules.objects.get(ruleid=device_rule.ruleid,isAction=True,device_id=self.device.id,isControlDevice=False)
        except AliyunIotRules.DoesNotExist:
            return
        self._aliyun.delete_rule_action(device_action.action_id)
        device_action.delete()

    def create_rule_action(self,relu_id,configuration,device_id,is_control):
        """
        Create Aliyun IoT rule action
        Only one action per device or control device in each rule
        :param relu_id:
        :param configuration:
        :param device_id:
        :param is_control:
        :return: The action object
        """
        if not AliyunIotRules.objects.filter(ruleid=relu_id,action_config=configuration,isAction=True,device_id=device_id,isControlDevice=is_control).exists():
            data = self._aliyun.create_rule_action(relu_id,configuration)
            if data is not None:
                aliyun_iot_relu_ = AliyunIotRules(
                    name=str(relu_id) + '_action_',
                    ruleid=relu_id,
                    isAction=True,
                    device_id=device_id,
                    action_id=data["ActionId"],
                    isControlDevice=is_control,
                    requestid=data["RequestId"],
                    action_type="REPUBLISH",
                    action_config=configuration,
                )
                aliyun_iot_relu_.save()
        return AliyunIotRules.objects.get(ruleid=relu_id,action_config=configuration,isAction=True,device_id=device_id,isControlDevice=is_control)


    def create_rule(self,rule_name,topic,product_key,device_id,is_control):
        """
        Create Aliyun IoT rule
        It will only be created once for each device or control device
        :param rule_name:
        :param topic:
        :param product_key:
        :param device_id:
        :param is_control: if there is the control device's rule
        :return: The device's rule
        """
        if not AliyunIotRules.objects.filter(short_topic=topic,isControlDevice=is_control,device_id=device_id).exists():
            data = self._aliyun.create_rule(rule_name=rule_name,topic=topic,product_key=product_key)

            if data is not None:
                aliyun_iot_relu = AliyunIotRules(
                    name=rule_name,
                    short_topic=topic,
                    ruleid=data["RuleId"],
                    isControlDevice=is_control,
                    device_id=device_id,
                    requestid=data["RequestId"]
                )
                aliyun_iot_relu.save()
                # self._aliyun.start_rule(data["RuleId"])

        return AliyunIotRules.objects.get(short_topic=topic,isControlDevice=is_control,device_id=device_id)

    def __md5(self,str):
        m = hashlib.md5()
        m.update(str.encode("utf8"))
        return m.hexdigest()[8:-8] + ''.join(random.sample(string.ascii_letters + string.digits, 4))


def check_login(request):
    userid = request.session.get('userid')
    if userid is None:
        return False
    return True