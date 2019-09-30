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



from django.contrib.auth.models import User
from django.http import HttpResponseNotAllowed
from django.views.generic import TemplateView
import requests

from common.config import WECHAT_APPID, WECHAT_SECRET, OPENID_OR_UNIONID, BASE_URL


class WechatCommonView(TemplateView):
    """
    The parent view for Wechat login
    """

    def get(self, request, *args, **kwargs):
        """
        Get Wechat user info, can only recall the url in Wechat client
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        code = request.GET.get('code', None)
        state = request.GET.get('state', None)
        self.full_url = BASE_URL + request.get_full_path()

        if code is None:
            return HttpResponseNotAllowed('<h1> Not Allowed </h1>')
        user_data = requests.get(
            'https://api.weixin.qq.com/sns/oauth2/access_token?appid=' + WECHAT_APPID + '&secret=' + WECHAT_SECRET + '&code=' + code + '&grant_type=authorization_code').json()
        access_token = user_data.get('access_token')
        openid = user_data.get('openid')
        if openid is None:
            return HttpResponseNotAllowed('<h1> Not Allowed </h1>')
        user_data = requests.get(
            'https://api.weixin.qq.com/sns/userinfo?access_token=' + access_token + '&openid=' + openid + '&lang=zh_CN')
        user_data.encoding = 'utf-8'
        user_data = user_data.json()
        unionid = user_data.get(OPENID_OR_UNIONID)

        try:
            user = User.objects.get(username=unionid)
        except User.DoesNotExist:
            user = User(
                username=unionid,
                first_name=user_data.get('nickname', 'kessk user'),
                email=user_data.get('headimgurl'),
            )
            user.save()
        user = User.objects.get(username=unionid)

        request.session['userid'] = user.id
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

