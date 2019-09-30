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



import base64
import hashlib
import json
import random
import string
from datetime import datetime

import pytz
import requests
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.decorators import api_view

from common.AliyunIot import AliyunIot
from common.ExceptionAPI import AValidation400Error, response_json
from common.WechatCommonView import WechatCommonView
from common.config import ErrorCodes, BASE_URL, QRCODE_API, QRCODE_TIME_OUTS, WECHAT_APPID
from device.models import DeviceBind, ControlDevice, Device, DeviceVersion
from device.serializers import DeviceSerializers
from device.views import ControlDeviceAction, check_login, DeviceBindAction
from user.models import UserConfig


class UserIndex(WechatCommonView):

    """
    User index to control devices
    """
    template_name = "index-weui.html"

    def get(self, request, *args, **kwargs):
        super().get(request,*args,**kwargs)

        context = self.get_context_data(**kwargs)

        try:
            user = User.objects.get(id=request.session.get('userid'))
            devices = DeviceBind.objects.filter(user=user,onActive=True)
            device_version = DeviceVersion.objects.latest("version_num")
            user_config = UserConfig.objects.get(user=user)
        except DeviceBind.DoesNotExist:
            devices = []
        except UserConfig.DoesNotExist:
            user_config = None

        control_action = ControlDeviceAction(user=user)
        control_device = control_action.create_control_device()
        aliyun_client = AliyunIot()
        devices = aliyun_client.get_muti_device_status(devices)
        context["user"] = user
        context["devices"] = devices
        context["new_version_num"] = device_version.version_num
        update_device_count = 0
        device_list = {}
        for device in devices:
            d = {}
            if device_version.version_num > device.device.device_version :
                update_device_count += 1
            d["status"] = device.onActive
            d["version"] = device.device.device_version
            d["device_name"] = device.device.device_name
            d["device_update"] = device_version.version_num > device.device.device_version
            d["binding_date"] = device.bind_time.strftime("%Y/%m/%d, %H:%M:%S")
            d["nick_name"] = device.device_name
            d["onActive"] = device.onActive
            d["new_version_num"] = device_version.version_num
            if device.origin_user is not None:
                d["is_share"] = True
                d["share_from"] = device.origin_user.first_name
            else:
                d["is_share"] = False
            device_list[device.device.device_name] = d
            # device_list[device.device.device_name+'2'] = d
        device_json = json.dumps(device_list)
        context["control_device"] = control_device
        context["update_device_count"] = update_device_count
        context["device_json"] = device_json
        context["user_config"] = user_config
        return self.render_to_response(context)


class UserShare(WechatCommonView):

    template_name = "share.html"

    def get(self, request, *args, **kwargs):
        state = request.GET.get("state")
        code = request.GET.get("code")
        share_code = request.GET.get("share_code")
        if state is None and code is None and share_code is not None:
            return redirect(
                'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + WECHAT_APPID + '&redirect_uri='+BASE_URL+'/user/share/?share_code='+ share_code +'&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect')

        super().get(request, *args, **kwargs)
        context = self.get_context_data(**kwargs)

        # Check if the share code has out of time
        share_info = cache.get(share_code)

        if share_info is None :
            self.template_name = "share_faild.html"
            return self.render_to_response(context)
        user_id = share_info.get("user")
        device_id = share_info.get("device")

        try:
            user = User.objects.get(id=user_id)
            device = Device.objects.get(id=device_id)
            device_bind = DeviceBind.objects.get(user=user,device=device,onActive=True)
        except User.DoesNotExist or Device.DoesNotExist or DeviceBind.DoesNotExist:
            self.template_name = "share_faild.html"
            return self.render_to_response(context)


        # if is the same user
        if request.session.get('userid') == int(user_id) or DeviceBind.objects.filter(user_id=request.session.get('userid'),device=device,onActive=True).exists():
            return redirect(
                'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + WECHAT_APPID + '&redirect_uri=' + BASE_URL + '/user/index/&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect')

        # device_action = DeviceBindAction(device=device, user=current_user)
        # device_bind = device_action.bind_device(origin_user=user)

        context["user"] = user
        context["device"] = device_bind
        context["share_code"] = share_code


        return self.render_to_response(context)

@api_view(['POST'])
def get_share_qrcode(request):
    if not check_login(request):
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['not_allowed'],
                                  errcode=ErrorCodes['global']['not_allowed'])
    # request.session["userid"] = 2
    device_id = request.POST.get('device_id')
    if not device_id:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['required'],
                                  errcode=ErrorCodes['global']['required'])
    user = User.objects.get(id=request.session.get("userid"))
    try:
        device = Device.objects.get(device_name=device_id)
        device_bind = DeviceBind.objects.get(device=device,user=user,onActive=True)
    except Device.DoesNotExist or DeviceBind.DoesNotExist:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['not_allowed'],
                                  errcode=ErrorCodes['global']['not_allowed'])


    code = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    code += str(user.id)
    code += str(device.id)
    m = hashlib.md5()
    m.update(code.encode("utf8"))
    code = m.hexdigest()
    cache.set(code,{
        "user" : user.id,
        "device" : device.id
    },QRCODE_TIME_OUTS)
    print(code)
    url = QRCODE_API + BASE_URL + '/user/share/?share_code=' + code
    return JsonResponse(response_json(data={"url": url}),
                        status=status.HTTP_201_CREATED)

@api_view(["POST"])
def get_device_users(request):
    if not check_login(request):
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['not_allowed'],
                                  errcode=ErrorCodes['global']['not_allowed'])
    device_name = request.POST.get('device_name')
    if not device_name:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['required'],
                                  errcode=ErrorCodes['global']['required'])
    user = User.objects.get(id=request.session.get("userid"))
    device_bind = DeviceBind.objects.get(user=user,device__device_name=device_name, onActive=True)
    device_binds = DeviceBind.objects.filter(device=device_bind.device,onActive=True).order_by("origin_user")
    serialize_data = DeviceSerializers(device_binds,many=True)
    return JsonResponse(response_json(data=serialize_data.data),
                        status=status.HTTP_201_CREATED)

@api_view(["POST"])
def unbinding_device(request):
    if not check_login(request):
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['not_allowed'],
                                  errcode=ErrorCodes['global']['not_allowed'])
    device_name = request.POST.get('device_name')
    if not device_name:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['required'],
                                  errcode=ErrorCodes['global']['required'])
    user = User.objects.get(id=request.session.get("userid"))
    try:
        device_bind = DeviceBind.objects.get(user=user, device__device_name=device_name, onActive=True)
    except DeviceBind.DoesNotExist:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['user']['not_binding'],
                                  errcode=ErrorCodes['user']['not_binding'])
    device_action = DeviceBindAction(device=device_bind.device, user=user)
    device_action.unbind_user_device()
    return JsonResponse(response_json(data={}),
                        status=status.HTTP_201_CREATED)


@api_view(["POST"])
def upgrade_device_done(request):
    if not check_login(request):
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['not_allowed'],
                                  errcode=ErrorCodes['global']['not_allowed'])
    device_name = request.POST.get('device_name')
    version = request.POST.get('version')
    if not device_name or not version:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['required'],
                                  errcode=ErrorCodes['global']['required'])
    user = User.objects.get(id=request.session.get("userid"))
    try:
        device_bind = DeviceBind.objects.get(user=user, device__device_name=device_name, onActive=True)
    except DeviceBind.DoesNotExist:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['user']['not_binding'],
                                  errcode=ErrorCodes['user']['not_binding'])
    device_bind.device.device_version = version
    device_bind.device.save(update_fields=['device_version'])
    return JsonResponse(response_json(data={}),
                        status=status.HTTP_201_CREATED)

@api_view(["POST"])
def change_user_index(request):
    if not check_login(request):
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['not_allowed'],
                                  errcode=ErrorCodes['global']['not_allowed'])
    device_name = request.POST.get('device_name')
    if not device_name:
        raise AValidation400Error(detail="Unknow", code=ErrorCodes['global']['required'],
                                  errcode=ErrorCodes['global']['required'])
    user = User.objects.get(id=request.session.get("userid"))
    try:
        device_bind = DeviceBind.objects.get(user=user, device__device_name=device_name, onActive=True)
    except DeviceBind.DoesNotExist:
        device_bind = None

    try:
        user_config = UserConfig.objects.get(user=user)
        user_config.index_device = device_bind
        user_config.save(update_fields=['index_device'])
    except UserConfig.DoesNotExist:
        user_config = UserConfig(
            user=user,
            index_device=device_bind
        )
        user_config.save()

    return JsonResponse(response_json(data={}),
                        status=status.HTTP_201_CREATED)


