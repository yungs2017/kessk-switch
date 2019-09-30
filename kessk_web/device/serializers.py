from django.contrib.auth.models import User
from  rest_framework import serializers

from device.models import DeviceBind, Device


class DeviceSerializers(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source="user.first_name")
    user_headimg = serializers.CharField(source="user.email")
    origin_nickname = serializers.CharField(source="origin_user.first_name",allow_null=True)
    origin_headimg = serializers.CharField(source="origin_user.email",allow_null=True)
    bind_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    
    class Meta:
        model = DeviceBind
        fields = ['user_nickname','user_headimg',  'origin_nickname', 'origin_headimg', 'bind_time']


