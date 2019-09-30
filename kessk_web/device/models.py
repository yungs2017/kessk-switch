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



from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Device(models.Model):
    """
    Device table model
    """
    device_name = models.CharField(u'Device name',max_length=128)
    device_type = models.CharField(u'Device type',max_length=20,null=True)
    product_key = models.CharField(u'Product Key',max_length=128,null=True)
    device_chipid = models.CharField(u'Device chip ID', max_length=64)
    product_name = models.CharField(u'Product name', max_length=64,null=True)
    device_version = models.IntegerField(u'Device fireware version number',null=True)
    add_time = models.DateTimeField(u'Device add time',auto_now_add=True)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.device_name

class DeviceBind(models.Model):
    """
    Device binding log
    """
    device = models.ForeignKey(Device,blank=True, on_delete=models.PROTECT)
    user = models.ForeignKey(User,blank=True, on_delete=models.PROTECT,related_name='user')
    origin_user = models.ForeignKey(User,blank=True,null=True, on_delete=models.PROTECT,related_name='origin_user')
    device_name = models.CharField(u'Device nickname',max_length=128,null=True)
    bind_time = models.DateTimeField(u'Bind time',auto_now_add=True)
    unbind_time = models.DateTimeField(u'Unbind time',blank=True,null=True)
    onActive = models.BooleanField(u'Active')


    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.device_name


class ControlDevice(models.Model):
    """
    Control Device table
    """
    product_name = models.CharField(u'Product Name',max_length=32,null=True)
    device_name = models.CharField(u'Device Name',max_length=64,null=True)
    user = models.ForeignKey(User,blank=True,null=True,on_delete=models.PROTECT)
    product_key = models.CharField(u'Product Key',max_length=128)
    device_secret = models.CharField(u'Device Secret',max_length=128)
    add_time = models.DateTimeField(u'Add Date',auto_now_add=True)
    device_type = models.IntegerField(u'Device Type',default=1)
    device_version = models.IntegerField(u'Device Version',default=1)

    def __str__(self):
        return self.device_name

class AliyunIotRules(models.Model):
    """
    Save Aliyun Iot message rules log
    """
    ruleid = models.CharField(u'Rule Id',max_length=128,null=True)
    requestid = models.CharField(u'Request Id',max_length=128,null=True)
    isAction = models.BooleanField(u'Rule or Action',default=False)
    isControlDevice = models.BooleanField(u'if control device',default=False)
    device_id = models.IntegerField(u'Device ID',null=True)
    short_topic = models.CharField(u'Short Topic',max_length=255,null=True)
    select_desc = models.CharField(u'Select',max_length=255,null=True)
    where_desc = models.CharField(u'Where',max_length=255,null=True)
    action_type = models.CharField(u'Action Type',max_length=16,null=True)
    action_id = models.CharField(u'Action ID',max_length=128,null=True)
    action_config = models.CharField(u'Action Configuration',max_length=128,null=True)
    add_time = models.DateTimeField(u'Add Time',auto_now_add=True)
    last_action_time = models.DateTimeField(u'Action Time',auto_now_add=True)
    name = models.CharField(u'Name',max_length=128,null=True)


    def __str__(self):
        return self.name

class DeviceVersion(models.Model):
    version_num = models.IntegerField(u'Version Number')
    version_detail = models.TextField(u'Version Detail',max_length=255,null=True)
    add_time = models.DateTimeField(u'Version Add Date',auto_now_add=True)

    # def __str__(self):
    #     return self.version_num



