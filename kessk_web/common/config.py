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


# Config file
# You must configure the following before you can run the project.

WECHAT_APPID = 'your wechat appid'
WECHAT_SECRET = 'wechat secret'
OPENID_OR_UNIONID = 'unionid' # important
WECHAT_GET_JSSDK_TICKET_URL = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?type=jsapi&access_token='
WECHAT_GET_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'%(WECHAT_APPID,WECHAT_SECRET)
BASE_URL = 'https://xxx.ngrok2.xiaomiqiu.cn'  # Your project url

ALIYUN_ACCESS_KEY = 'Aliyun access key'
ALIYUN_ACCESS_SECRET = 'Aliyun access secret'

ALIYUN_IOT_REGION = 'cn-shanghai'
ALIYUN_IOT_CONTROL_APP_PRODUCT_KEY = 'Control product key in aliyun IoT'
ALIYUN_IOT_ESP8266_PRODUCT_NAME = 'Esp8266 device product name in aliyun IoT'

DEVICE_MASK = 'KessK_WifiModule_'
DEVICE_NAME_DEFAULT = '开关'

QRCODE_API = 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data='
QRCODE_TIME_OUTS = 100 * 60


## Error code
ErrorCodes = {
    'global' : {
        'required' : 10000,
        'not_allowed' : 10010
    },
    'user' : {
        'not_exits' : 20000,
        'not_binding' : 20010
    },
    'device' : {
        'not_exits' : 30000,
        'share_oft' : 30010
    },
}