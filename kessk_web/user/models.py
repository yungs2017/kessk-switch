from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from device.models import DeviceBind


class UserConfig(models.Model):
    user = models.ForeignKey(User,null=True,on_delete=models.PROTECT)
    index_device = models.ForeignKey(DeviceBind,null=True,on_delete=models.PROTECT)
    add_time = models.DateTimeField(u'Add Time',auto_now_add=True)