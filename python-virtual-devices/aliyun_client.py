#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


from linkkit import linkkit


class Aliyun:


    def __init__(self,
                 product_key,
                 device_name,
                 device_secret
                 ):
        self.lk = linkkit.LinkKit(
            host_name="cn-shanghai",
            product_key=product_key,
            device_name=device_name,
            device_secret=device_secret)
        self._deviceName = device_name
        self.topic_get = 'user/get'
        self.topic_set = 'user/update'
        self.name = 'Client'
        self.lk.on_connect = self.on_connect
        self.lk.on_disconnect = self.on_disconnect
        self.lk.on_subscribe_topic = self.on_subscribe_topic
        self.lk.on_topic_message = self.on_topic_message
        self.lk.on_publish_topic = self.on_publish_topic

    def on_connect(self,session_flag, rc, userdata):
        print(self.name + " on_connect:%d,rc:%d,userdata:" % (session_flag, rc))
        rc, mid = self.lk.subscribe_topic(self.lk.to_full_topic(self.topic_get))

    def on_topic_message(self,topic, payload, qos, userdata):
        print(self.name + " on_topic_message:" + topic + " payload:" + str(payload) + " qos:" + str(qos))

    def on_disconnect(self,rc, userdata):
        print( self.name + " on_disconnect:rc:%d,userdata:" % rc)

    def on_subscribe_topic(self,mid, granted_qos, userdata):
        print(self.name + " on_subscribe_topic mid:%d, granted_qos:%s" %
              (mid, str(','.join('%s' % it for it in granted_qos))))
        pass

    def on_publish_topic(self,mid, userdata):
        print(self.name + " on_publish_topic mid:%d" % mid)

    def push_message(self,message):
        rc, mid = self.lk.publish_topic(self.lk.to_full_topic(self.topic_set), message)

    def connect(self):
        self.lk.connect_async()
        self.lk.start_worker_loop()