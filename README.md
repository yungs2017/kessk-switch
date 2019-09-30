# KeesK 智能开关
本项目旨在构建一款基于ESP8266的远程控制智能开关方案，方便个人或者企业简单快速实现一套远程控制开关程序。  
- 了解目前主流的智能开关以及智能化控制设备的工作原理和流程。  
- 了解ESP8266芯片的配网过程。
- 快速构建智能控制设备。
- 使用微信的airkiss协议进行配网。
- 使用阿里云IoT平台进行对消息进行发送和接收。

## 项目结构  
- kessk-device ： ESP8266的运行库文件  
- kessk_web ： 基于Django编写的后端和控制页面    
- python-virtual-devices ： python虚拟设备

## 项目预览  
视频加载缓慢请移步到 /images/video 下载
#### 设备绑定
<img src="https://github.com/yungs2017/kessk-switch/blob/master/images/device_bind_ui.jpeg" width="30%">
<video id="video" controls="" preload="none">
      <source id="mp4" src="https://github.com/yungs2017/kessk-switch/blob/master/images/video/device_bind.mp4?raw=true"
      <p>无法加载视频，请在 /images/video 下载</p>
</video>  

#### 设备控制  

<video id="video" controls="" preload="none">
      <source id="mp4" src="https://github.com/yungs2017/kessk-switch/blob/master/images/video/device_control.mp4?raw=true"
      <p>无法加载视频，请在 /images/video 下载</p>
</video>

#### 分享设备绑定  
<video id="video" controls="" preload="none">
      <source id="mp4" src="https://github.com/yungs2017/kessk-switch/blob/master/images/video/share_bind.mp4?raw=true"
      <p>无法加载视频，请在 /images/video 下载</p>
</video>  

<video id="video" controls="" preload="none">
      <source id="mp4" src="https://github.com/yungs2017/kessk-switch/blob/master/images/video/device_share.mp4?raw=true"
      <p>无法加载视频，请在 /images/video 下载</p>
</video>

#### 设备详情  
<img src="https://github.com/yungs2017/kessk-switch/blob/master/images/device-c-index.jpg" width="30%">

#### 设备OTA升级  
<img src="https://github.com/yungs2017/kessk-switch/blob/master/images/device-upgrade.jpg" width="30%">

#### 硬件预览  
<img src="https://github.com/yungs2017/kessk-switch/blob/master/images/switch-001.jpg" width="30%">
<img src="https://github.com/yungs2017/kessk-switch/blob/master/images/switch-002.jpg" width="30%">

#### 物料清单  

- ESP01S 继电器集成模块，集成了ESP01和一路继电器。估计零售价为6-10元RMB

- 触控开关模块，零售价约为1-2元RMB

- AC转DC电源模块，零售价约为2-5元RMB  

- DC-DC电源模块，用于稳压/升压/降压。如果转换电源或者ESP8266外围中已经集成则不需要该模块

- 触控开关面板，零售价约为3-8元RMB
  
##流程原理  
- 用户通过扫码或者链接形式访问设备绑定页面（在微信内）
- 根据提示使得需要配网的设备进入配网状态（smartconfig状态）  
- 点击配网，使用微信的jssdk调起airkiss原生页面，用户输入当前手机链接的Wi-Fi密码  
- 设备通过airkiss配网成功
- 手机端web页面通过微信jssdk调起扫描附近Wi-Fi设备的功能  
- 设备接收到扫描请求，返回设备的唯一识别码（这里定义为设备的MAC地址）  
- 手机web页面接收到设备唯一识别码，请求后端API绑定用户与设备之间的关系，后端返回该设备的阿里云iot平台的device_name 
- 提示用户输入设备的名称（可选）  
- 进入控制页面，对设备进行控制  
> 设备端与控制端通过阿里云iot平台的MQTT协议进行实时通讯，通过阿里云iot平台的数据流规则绑定设备与对应控制端的通讯关系（订阅和推送topic之间的关系），也可以通过阿里云iot的消息路由实现。  
##### 设备绑定流程  
<img src="https://github.com/yungs2017/kessk-switch/blob/master/images/device_bind_flow.jpg" width="90%">  

##### 控制流程 
<img src="https://github.com/yungs2017/kessk-switch/blob/master/images/control_devices.jpg" width="100%">


## 服务端（Django）
###view入口  
- /device/bind/ 设备绑定
- /user/index/ 控制首页
- /user/share/ 分享绑定页面
- /api/device/bind/ 设备绑定请求API
- /api/device/ccname/ 更改设备名称API
- /api/user/share/ 分享二维码获取API
- /api/user/share/bind/ 分享绑定API
- /api/device/bind/log/ 获取设备的绑定用户API
- /api/device/unbind/ 解绑设备的API
- /api/device/update/ 设备版本更新API
- /api/user/ccindex/ 更改控制首页的API


### 依赖环境
- python3.7.6
- Django 2.2.4 
- djangorestframework 3.10.2 
- django_filter 2.2.0  
- aliyun-python-sdk-core
- aliyun-python-sdk-iot

## 设备端（ESP8266）
- 设备端使用ESP8266芯片作为控制，这里我用的是ESP01S。这个SOC只引出了GPIO0和GPIO2，本项目源码使用GPIO0作为控制继电器输出。使用RX作为触控模块的输入（RX为GPIO3）。因为ESP8266芯片在上电的时候IO0需要高电平，如果使用IO0则需要使用电阻串上3.3v比较麻烦，则直接使用了RX口。

## 功能列表
- 微信原生配网
- 微信内控制
- 可一键分享设备给微信好友进行绑定
- 多控制端实时控制设备并实时获取设备状态
- 进行OTA固件升级
- 每个绑定用户可创建不同设备名称
- 查看所有绑定该设备的用户
- 设备解绑
- 使用阿里云MQTT支持高并发可靠
- 可使用单一设备作为控制主页
- 延时操作（未完成）
- 定时任务（未完成）

## 部署运行
### 首先需要的条件
1. 阿里云iot平台账号。可以使用淘宝或者阿里账户开通，免费。消息转发根据消息量和设备在线时间进行收费，费用很低。以下摘自官方的计费示例 https://help.aliyun.com/document_detail/73701.html
> 假设 有10,000台设备，每台设备每天在线时长8小时；每台设备每分钟发送一条消息，且每条消息大小不超过0.5 KB。当月有30天。
计费方法：
    消息通信费用计算
    当月消息数量：60×8×30×10,000=144,000,000条。
    当月通信费计算：1,000,000条为免费消息；99,000,000条的计费标准是1.8元/1,000,000条；44,000,000条的计费标准是1.4元/1,000,000条，所以通信费用为：1×0+99×1.8+44×1.4=239.8元。
    设备连接时长费用计算
    当月设备连接分钟数：60×8×30×10,000=144,000,000分钟。
    当月设备连接时长计费标准为1元/1,000,000分钟，前1,000,000分钟为免费，所以连接时长费用为：1×0+143×1=143元。
    当月总费用：239.8+143=382.8元。
2. python3.7 以及 安装了pip，各平台安装请自行解决。
3. 微信公众号。如果没有可以使用微信提供的测试公众号，申请入口：https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login
4. 动态域名解析或者内网穿透工具。因为微信公众号开发的时候需要提供备案的域名作为授权的调取URL。这里推荐米球ngrok：http://www.xiaomiqiu.cn/
6. 修改微信公众号的“网页授权获取用户信息”的授权网址更改为实际访问Django项目的地址。
7. 修改微信公众号的js安全域名为实际访问Django的项目地址。
8. 如果是正式的微信公众号（非测试公众号）则需要在公众号的设置中设置IP白名单为当前运行Django主机的IP地址（本机的外网IP地址）。
9.ESP8266 SOC以及烧录工具。也可以执行本项目的 virtual device 进行虚拟一个python下的设备。由于是虚拟的，所以不能进行配网操作，所以需要自己去阿里云转发规则中手动创建转发规则进行体验。
10. 一路继电器驱动模块。
11. 电容触摸控制模块或者其他触控模块。
12. 杜邦线或者连接线。  
追加说明：因为需要调用微信的airkiss功能，所以请在微信公众号内打开“设备”功能。  
<img src="https://github.com/yungs2017/kessk-switch/blob/master/images/wx-device.jpg" width="30%">  
设置微信公众号的安全js地址/web授权url以及白名单（测试号无需设置IP白名单）  
<img src="https://github.com/yungs2017/kessk-switch/blob/master/images/wx-web-js-url.jpg" width="30%">
<img src="https://github.com/yungs2017/kessk-switch/blob/master/images/ip_write.jpg" width="30%">

### 运行
1. git clone 
2. cd 
3. pip install requirements.txt   
4. 去阿里云物联网平台创建产品和设备，需要创建两个产品，并且每个设备（ESP8266设备）均需要在阿里云上面创建一个对应的设备。如何创建产品和设备https://help.aliyun.com/document_detail/73728.html
> 需要针对设备端（ESP8266）和控制端创建产品，产品的名称自定义（下面在Django配置文件中需要使用）。
> 由于使用的是“一机一密”的方式连接到阿里云物联网平台，所以每个设备均需要预先在阿里云平台创建对应的设备。控制端（手机端）则不需要，会在代码中进行自动创建。
5. 修改项目中的Django的配置文件内容（位于：/kessk_web/common/config.py）    

```python
WECHAT_APPID = '微信公众号的appid'
WECHAT_SECRET = '微信公众好的secret'
OPENID_OR_UNIONID = 'unionid'  # 这里特别注意，只有你的公众号下绑定了微信开放平台或者小程序才会有unionid，否则请更改为openid
BASE_URL = 'https://xxx.ngrok2.xiaomiqiu.cn' # 这里是你的公网url，也就是通过这个url访问到的Django的网址
ALIYUN_ACCESS_KEY = '阿里云的access_token' # 如果是子账号的access_token 则请确保该子账号拥有物联网平台的权限
ALIYUN_ACCESS_SECRET = '阿里云的access_secret'

ALIYUN_IOT_REGION = 'cn-shanghai'  #阿里云物联网所在的区域
ALIYUN_IOT_CONTROL_APP_PRODUCT_KEY = '控制端设备的产品key'
ALIYUN_IOT_ESP8266_PRODUCT_NAME = '设备的产品key'
```
6. python  运行Django，使用默认的8000端口
7. 请配置ngrok并将ngrok服务映射为本地的8000端口，以下是我的配置文件，仅供参考。

```bash
server_addr: "ngrok2.xiaomiqiu.cn:5432"
trust_host_root_certs: true
inspect_addr: disabled
auth_token: "your token"
tunnels:
    httptun:
      remote_port: 80
      subdomain: airless
      proto:
        http: 127.0.0.1:8000
    httpstun:
      remote_port: 443
      subdomain: airless
      proto:
        https: 127.0.0.1:8000
    tcptun:
      remote_port: 81
      proto:
        tcp: 127.0.0.1:81
```
8. 浏览器进入Django的后台：http://127.0.0.1:8000/admin/ 使用账号 admin 密码：admin 登录。
9. 进入/device/device 下创建一个设备，这个设备需要和阿里云中创建的设备相对应。
> Device name ： 这个设备在阿里云物联网中的device name，上面步骤创建设备的时候对应分配的device name
> Product Key ： 这个设备在阿里云物联网中的product key，可以在设备详情页面查看获得。
> Device chip ID ： 这个设备的Mac地址，因为绑定设备的时候会根据这个参数判断用户绑定的设备是哪一个，所以这个Mac地址十分重要，例如ESP8266的Mac地址是：07:16:76:00:02:86,则这里填入071676000286
> Product name ：对应设备在阿里云物联网中的product name，上面步骤创建产品时候输入的名称。
> Device fireware version number ： 设备的固件版本，自定义。
补充：需要在阿里云物联网平台中创建一条转发规则，将控制端的消息发送给设备，格式按照下面的进行：  
<img src="https://github.com/yungs2017/kessk-switch/blob/master/images/aliyun-iot-rule.jpg" width="30%">
10. 安装并打开Arduino IDE，安装ESP8266 的支持，具体请自行搜索。
11. 安装Arduino的MQTT依赖以及 Arduino json依赖，具体请自行搜索。
12. 打开项目的 /kessk-devices/kessk-devices.ino 修改头文件的设备名称和产品名称（对应阿里云物联网平台的设备名称和秘钥以及产品名称），连接上烧录器以及ESP8266 进行固件烧录。
13. 将触控开关连接到SOC的GPIO3（RX），继电器控制线连接到GPIO0。
14.手机微信内打开：https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx8dc705a03c99a21f&redirect_uri=https://xxx.ngrok2.xiaomiqiu.cn/device/bind/&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect
> 上述连接中的：https://xxx.ngrok2.xiaomiqiu.cn 请更改为实际的Django访问连接。
15. 根据提示绑定以及控制设备体验。
> 设备进行OTA升级的时候会从固定的地址按照版本号码的规律以及Mac地址搜寻对应的升级固件，请配置kessk-devices中的头文件中的“UPGRADE_URL”为实际的升级包路径。这里我将升级包文件放在了阿里云的OSS中并设置了访问的限制。
####针对虚拟设备
为了方便测试提供了python下写的虚拟设备，如果没有实际ESP8266设备在手的可以通过以下的步骤进行体验测试。
1. 上面的步骤1～9仍然是必须的。
2. 打开本项目的： /python-virtual-devices/device.py，修改配置内容：
```python
    def __init__(self):
        Aliyun.__init__(self,product_key='产品的key',
                 device_name='设备名称',
                 device_secret='设备秘钥')
        self.name = "Client ESP8266"
```
3. 去阿里云物联网平台创建一个转发规则，主要是将该设备的消息转发到控制端。详细参考：https://help.aliyun.com/document_detail/42734.html
4. 运行虚拟设备：python device.py
5.可以在终端下输入 on/off 来模拟控制设备的开关状态。
6. 手机微信内打开：https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx8dc705a03c99a21f&redirect_uri=https://xxx.ngrok2.xiaomiqiu.cn/device/bind/&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect 进行控制。
> 上述连接中的：https://xxx.ngrok2.xiaomiqiu.cn 请更改为实际的Django访问连接。

## 功能扩展
- 延迟开关功能
- 快关定时任务
- 使用smartconfig 实现不配网的情况下使用手机进行控制开关
- 多路继电器开关
- 智能插座
- 网关接入
- 智能音箱控制接入
- 使用已配网的设备快速对新的设备进行配网
- 异常监控
- 温度监测  
- 单火/单零供电

## 可能出现的问题
- 无法获取 js ticket ： 请检查是否正确配置微信公众号（Django配置文件）以及微信公众号内的设置是否正确的配置了js安全域名和IP白名单。
- 用户无法注册登录： 请检查是否正确配置微信公众号的信息，并且 OPENID_OR_UNIONID 是否正确（如设置为unionid，但实际上公众号没有该数据，通常一个公众号没有绑定开放平台或者没有小程序的情况下不会存在这个字段，推荐使用openid进行测试）。
- 无法远程控制设备的状态： 请确保阿里云的access_token拥有操作物联网平台的权限。并检查创建的转发规则是否正确。
- 可以远程操作设备，但是无法正常获取设备的状态。请检查物联网的转发规则是否有错。
- ESP8266 烧录固件失败，请检查Arduino烧录参数是否与芯片相匹配。
- 无法正常绑定设备：请检查数据表（devices）中的相关字段和物联网平台的是否一致并且Mac地址是否一致。由于ESP8266目前仅支持2.4G的Wi-Fi，所以配网的时候请将手机连接到非5G的Wi-Fi，配网的时候需要关闭手机的所有VPN连接。

## 产品建议
如果要部署产品，建议进行以下修改
- 不建议使用目前的H5的方式进行远程控制。因为H5中使用js连接阿里云的MQTT服务器，会暴露控制端的参数。建议更改为小程序或者app的方式进行控制。可以在配网成功后引导用户进入小程序。
- 建议更改MQTT信息的QoS值，以确保设备能够正确的获取到控制端的信息。
- 建议将目前的“一机一密”更改为“一型一密”，这样就可以在批量烧录设备的时候无需事先配置固件的设备信息。关于阿里云的“一型一密”可以参考：https://help.aliyun.com/document_detail/74006.html
- 绑定设备的时候添加控制端（请求绑定的手机）接收到设备信息并返回以确保控制端接收到设备的信息后才关闭消息的传送。

## 参见
- 阿里云物联网平台：https://help.aliyun.com/product/30520.html
- ESP8266 smartconfig ： 
- 微信airkiss ： https://iot.weixin.qq.com/wiki/new/index.html
- https://github.com/yulong88888/Arduino_ESP8266_WeChat_AirkissAndNFF 本项目中的airkiss设备局域网发现功能部分代码参考该项目。

## License
#### [The 3-Clause BSD License](https://opensource.org/licenses/BSD-3-Clause)
> Copyright (C) 2019, KessK, all rights reserved.
Copyright (C) 2019, Kison.Y, all rights reserved.

> Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

> 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

> 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

> 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

> THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

