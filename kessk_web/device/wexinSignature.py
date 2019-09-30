import hashlib
import random
import string
import time
from django.core.cache import cache
import requests
from common.config import WECHAT_GET_JSSDK_TICKET_URL, WECHAT_GET_ACCESS_TOKEN_URL


class Signature:
    """
    Get Wechat JSSDK signature
    """

    def __init__(self,url):
        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': Base_authorization.get_ticket(),
            'timestamp': self.__create_timestamp(),
            'url': url
        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)]).encode('utf-8')
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        return self.ret


class Base_authorization():
    """
    Get JSSDK ticket and accesstoken
    Cache to Django table cache
    """

    @classmethod
    def get_ticket(cls):
        key = 'ticket'
        if cache.has_key(key):
            ticket  = cache.get(key)
        else:
            if cache.has_key('access_token'):
                access_token = cache.get('access_token')
            else:
                access_token = cls.get_access_token()
            ticket = requests.get(WECHAT_GET_JSSDK_TICKET_URL+access_token).json()['ticket']
            cache.set(key,ticket,110*60)
        return ticket

    @staticmethod
    def get_access_token():
        key = 'access_token'
        access_token = requests.get(WECHAT_GET_ACCESS_TOKEN_URL).json()['access_token']
        # print(access_token.text)
        cache.set(key,access_token,110*60)
        return access_token