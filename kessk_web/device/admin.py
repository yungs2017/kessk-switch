from django.contrib import admin

# Register your models here.
from device.models import Device, DeviceBind, ControlDevice, AliyunIotRules, DeviceVersion


class DeviceAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = (
    'id', 'device_name', 'device_type', 'device_chipid', 'product_name', 'device_version', 'add_time',
    )
    search_fields = ('device_name', 'device_type', 'device_chipid', 'product_name', 'device_version')

class DeviceBindAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = (
        'id','user','device_name','origin_user','device','bind_time','unbind_time','onActive'
    )
    search_fields = ('device_name', 'origin_user', 'device', 'bind_time', 'onActive')

class ControlDeviceAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = (
        'id', 'user', 'device_name', 'product_name', 'product_key', 'device_secret', 'add_time', 'device_type','device_version'
    )
    search_fields = ('device_name', 'product_name', 'device_type', 'device_version', 'user')

class AliyunIotRulesAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = [field.name for field in AliyunIotRules._meta.get_fields()]

class DeviceVersionAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = [field.name for field in DeviceVersion._meta.get_fields()]


admin.site.register(Device, DeviceAdmin)
admin.site.register(DeviceBind, DeviceBindAdmin)
admin.site.register(ControlDevice, ControlDeviceAdmin)
admin.site.register(AliyunIotRules, AliyunIotRulesAdmin)
admin.site.register(DeviceVersion, DeviceVersionAdmin)
