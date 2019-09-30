"""kessk_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from device.views import BindView, bindDevice, ccnameDevice, bindShareDevice
from user.views import UserIndex,  get_share_qrcode, UserShare, get_device_users, unbinding_device, upgrade_device_done, change_user_index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('device/bind/',BindView.as_view()),
    path('user/index/',UserIndex.as_view()),
    path('user/share/',UserShare.as_view()),
    path('api/device/bind/',bindDevice),
    path('api/device/ccname/',ccnameDevice),
    path('api/user/share/',get_share_qrcode),
    path('api/user/share/bind/',bindShareDevice),
    path('api/device/bind/log/',get_device_users),
    path('api/device/unbind/',unbinding_device),
    path('api/device/update/',upgrade_device_done),
    path('api/user/ccindex/',change_user_index),
]
