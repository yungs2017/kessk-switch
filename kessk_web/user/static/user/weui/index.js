$(function () {
    var pageManager = {
        $container: $('#container'),
        _pageStack: [],
        _configs: [],
        _pageAppend: function(){},
        _defaultPage: null,
        _defaultIndex:null,
        _pageIndex: 1,
        pageValues : null,
        setDefault: function (defaultPage) {
            this._defaultPage = this._find('name', defaultPage);
            return this;
        },
        setDetaultIndex : function (index) {
            if (index != null && index != '')
                this._defaultIndex = index;
            return this;
        },
        setPageAppend: function (pageAppend) {
            this._pageAppend = pageAppend;
            return this;
        },
        init: function () {
            var self = this;

            $(window).on('hashchange', function () {
                var state = history.state || {};
                var url = location.hash.indexOf('#') === 0 ? location.hash : '#';
                var page = self._find('url', url) || self._defaultPage;
                if (state._pageIndex <= self._pageIndex || self._findInStack(url)) {
                    self._back(page);
                } else {
                    self._go(page);
                }
            });

            if (history.state && history.state._pageIndex) {
                this._pageIndex = history.state._pageIndex;
            }

            this._pageIndex--;

            var url = location.hash.indexOf('#') === 0 ? location.hash : '#';
            var page = self._find('url', url) || self._defaultPage;
            console.log(url)
            console.log(page)
            if (this._defaultIndex) {
                this.go('device')
                $("title").html(GLOBAL_DEVICE_NAME)
            }
            else
                this._go(page);
            // this._go(self._defaultPage);


            return this;
        },
        push: function (config) {
            this._configs.push(config);
            return this;
        },
        go: function (to) {
            var config = this._find('name', to);
            if (!config) {
                return;
            }
            if (to == '#' || to == "home") {

                $("title").html("KessK控制主页")
            }
            location.hash = config.url;
        },
        _go: function (config) {
            this._pageIndex ++;

            history.replaceState && history.replaceState({_pageIndex: this._pageIndex}, '', location.href);

            var html = $(config.template).html();
            var $html = $(html).addClass('slideIn').addClass(config.name);
            $html.on('animationend webkitAnimationEnd', function(){
                $html.removeClass('slideIn').addClass('js_show');
            });
            this.$container.append($html);

            this._pageAppend.call(this, $html);

            this._pageStack.push({
                config: config,
                dom: $html
            });


            if (!config.isBind) {
                this._bind(config);
            }

            return this;
        },
        back: function () {
            history.back();
        },
        _back: function (config) {
            this._pageIndex --;

            var stack = this._pageStack.pop();
            if (!stack) {
                return;
            }

            var url = location.hash.indexOf('#') === 0 ? location.hash : '#';
            if (url == '#') {

                $("title").html("KessK控制主页")
            }
            var found = this._findInStack(url);
            if (!found) {
                var html = $(config.template).html();
                var $html = $(html).addClass('js_show').addClass(config.name);
                $html.insertBefore(stack.dom);

                if (!config.isBind) {
                    this._bind(config);
                }

                this._pageStack.push({
                    config: config,
                    dom: $html
                });
            }

            stack.dom.addClass('slideOut').on('animationend webkitAnimationEnd', function () {
                stack.dom.remove();
            });

            return this;
        },
        _findInStack: function (url) {
            var found = null;
            for(var i = 0, len = this._pageStack.length; i < len; i++){
                var stack = this._pageStack[i];
                if (stack.config.url === url) {
                    found = stack;
                    break;
                }
            }
            return found;
        },
        _find: function (key, value) {
            var page = null;
            for (var i = 0, len = this._configs.length; i < len; i++) {
                if (this._configs[i][key] === value) {
                    page = this._configs[i];
                    break;
                }
            }
            return page;
        },
        _bind: function (page) {
            var events = page.events || {};
            for (var t in events) {
                for (var type in events[t]) {
                    this.$container.on(type, t, events[t][type]);
                }
            }
            page.isBind = true;
        }
    };

    function fastClick(){
        var supportTouch = function(){
            try {
                document.createEvent("TouchEvent");
                return true;
            } catch (e) {
                return false;
            }
        }();
        var _old$On = $.fn.on;

        $.fn.on = function(){
            if(/click/.test(arguments[0]) && typeof arguments[1] == 'function' && supportTouch){ // 只扩展支持touch的当前元素的click事件
                var touchStartY, callback = arguments[1];
                _old$On.apply(this, ['touchstart', function(e){
                    touchStartY = e.changedTouches[0].clientY;
                }]);
                _old$On.apply(this, ['touchend', function(e){
                    if (Math.abs(e.changedTouches[0].clientY - touchStartY) > 10) return;

                    e.preventDefault();
                    callback.apply(this, [e]);
                }]);
            }else{
                _old$On.apply(this, arguments);
            }
            return this;
        };
    };

    function androidInputBugFix(){
        // .container 设置了 overflow 属性, 导致 Android 手机下输入框获取焦点时, 输入法挡住输入框的 bug
        // 相关 issue: https://github.com/weui/weui/issues/15
        // 解决方法:
        // 0. .container 去掉 overflow 属性, 但此 demo 下会引发别的问题
        // 1. 参考 http://stackoverflow.com/questions/23757345/android-does-not-correctly-scroll-on-input-focus-if-not-body-element
        //    Android 手机下, input 或 textarea 元素聚焦时, 主动滚一把
        if (/Android/gi.test(navigator.userAgent)) {
            window.addEventListener('resize', function () {
                if (document.activeElement.tagName == 'INPUT' || document.activeElement.tagName == 'TEXTAREA') {
                    window.setTimeout(function () {
                        document.activeElement.scrollIntoViewIfNeeded();
                    }, 0);
                }
            })
        }
    }

    function setPageManager(){
        var pages = {}, tpls = $('script[type="text/html"]');

        for (var i = 0, len = tpls.length; i < len; ++i) {
            var tpl = tpls[i], name = tpl.id.replace(/tpl_/, '');
            pages[name] = {
                name: name,
                url: '#' + name,
                template: '#' + tpl.id
            };
        }
        // pages.home.url = '#';
        pages.home.url = '#';
        console.log(pages)

        for (var page in pages) {
            pageManager.push(pages[page]);
        }

        pageManager
            .setPageAppend(function($html){
                var $foot = $html.find('.page__ft');
                if($foot.length < 1) return;

                var winH = $(window).height();
                if($foot.position().top + $foot.height() < winH){
                    $foot.addClass('j_bottom');
                }else{
                    $foot.removeClass('j_bottom');
                }
            })
            .setDefault('home')
            .setDetaultIndex(GLOBAL_INDEX)
            .init();
    }

    var deviceController = {
        _controlClient : null,
        _controlDeviceName : '',
        _devices : null,
        _dialog : {
            "cancelAndConfirmDialog" : $("#update-dialog"),
            "confirmDialog" : $("#global-iosDialog2"),
            "updateProgress" : $("#update-dialog .weui-progress"),
            "successToast" : $("#global-successToast"),
            "faildToast" : null,
            "loading" : $("#global-loadingToast")
        },
        _currentUpdateProgressObj : null,
        _getTopic : '',
        _updateTopic : '',
        _currentDeviceName : null,
        _totalUpdate : 0,
        _deviceListElements : $(".device-list-view"), // device list view
        _deviceMainControlElement : $(".device-main-control-view"), // device main control pannel

        init : function (c,d,e,f,g,h,i=null){
            this._controlClient = c
            this._controlDeviceName = d
            this._devices = e
            this._getTopic = f
            this._updateTopic = g
            this._totalUpdate = h
            this._controlClient.subscribe(this._getTopic);
            this._controlClient.on('connect', () => {
                console.log("Controller Connect Success")
                this.hideDialog()
                this._initDeviceStatus()
                // $("#loadingToast").hide()
                // get_devices_status()
            })
            this._controlClient.on('message', (topic, payload) => {
                this.handleDeviceTopicMsg(payload)
            });
            if (i != null && i != '') {
                this._currentDeviceName = i
                window.pageManager.pageValues = {
                "update" : window.deviceController.getSholdUpdate()
            }
            }
        },
        _handleClientMsg : function(){},
        _initDeviceStatus : function(){
            for (key in this._devices){
                // this._currentDeviceName = key
                this._pushGetDeviceStatusMsg(key)
            }
        },
        _getDeviceSwitchObj : function(){},


        _turnListDeviceStatus : function(device_name,value){
            /**
             * Turn on/off the device
             * @type {jQuery|HTMLElement}
             */
            var switchObj = $("#list-"+device_name + " input")
            console.log("list device view is")
            console.log(switchObj)
            var switchObjTips = $("#list-"+device_name + " .switch-label")
            switchObj.prop("checked",value)
            value ? switchObjTips.html("开") : switchObjTips.html("关")
            this._devices[device_name].status = value
        },
        _pushMsg : function(msg){
            this._controlClient.publish(this._updateTopic,msg)
        },
        _pushSwitchStatusChangeMsg : function () {
            var msg = '{"type":0,"status":'+ this._devices[this._currentDeviceName].status +',"control_device":"'+ this._controlDeviceName +'","deviceName":"'+ this._currentDeviceName +'"}'
            this._pushMsg(msg)
        },
        _pushGetDeviceStatusMsg : function (device_name) {
            var msg = '{"type":1,"status":1,"control_device":"'+ this._controlDeviceName +'","deviceName":"'+ device_name +'"}'
            this._pushMsg(msg)
        },
        _pushGetDeviceVersionMsg : function () {
            var msg = '{"type":3,"status":' + this._devices[this._currentDeviceName].new_version_num + ',"control_device":"'+ this._controlDeviceName +'","deviceName":"'+ this._currentDeviceName +'"}'
            this._pushMsg(msg)
        },
        _pushBeginDeviceUpdateMsg : function () {
            var msg = '{"type":6,"status":' + this._devices[this._currentDeviceName].new_version_num + ',"control_device":"'+ this._controlDeviceName +'","deviceName":"'+ this._currentDeviceName +'"}'
            console.log("Push update version message is : ")
            console.log(msg)
            this._pushMsg(msg)
        },
        devicePanelControl : function(){
            // this._devices[this._currentDeviceName].status = !this._devices[this._currentDeviceName].status
            if (this._devices[this._currentDeviceName].onActive){
                this.switch_device()
                this.changeDevicePanelStatus()
            }
            else
                $(".switch-text").html("设备已离线，无法进行控制")

        },
        changeDevicePanelStatus : function(){
            // if ($("title").html() != this._devices[this._currentDeviceName].nick_name)
            //     $("title").html(this._devices[this._currentDeviceName].nick_name)
            var tipsObj = $(".switch_status")
            var btObj = $(".switch-button")
            var ptObj = $(".status-point")
            var txObj = $(".switch-text")
            if (this._devices[this._currentDeviceName].status){
                btObj.addClass("switch-button-shadow")
                ptObj.addClass("background-green")
                btObj.html("ON")
                txObj.html("灯已开")
                tipsObj.html("开")
            }
            else {
                btObj.removeClass("switch-button-shadow")
                ptObj.removeClass("background-green")
                btObj.html("OFF")
                txObj.html("灯已关")
                tipsObj.html("关")
            }
            // if (!this._devices[this._currentDeviceName].onActive) {
            //     $(".power-buttons").attr("disabled","true")
            // }
        },
        switch_device : function(){
            this._turnListDeviceStatus(this._currentDeviceName,
                !this._devices[this._currentDeviceName].status)
            this._pushSwitchStatusChangeMsg()
        },
        handleDeviceTopicMsg : function (msg) {
            console.log("message reciver")

            msg = JSON.parse(msg.toString())
            console.log(msg)
            if (!this._devices[msg.device].onActive) {
                this._changeDeviceOnline(msg.device)
            }
            if (msg.type == 0){
                this._turnListDeviceStatus(msg.device,msg.status)
                if (msg.device == this._currentDeviceName)
                    this.changeDevicePanelStatus()
                if (msg.device == this._currentDeviceName && this._devices[msg.device].version < msg.version){
                    this._updateFinishRequestServer()
                }
            }
            else if (msg.type == 3) {
                // Device updating message
                console.log("Now newer version number is : ")
                console.log(this._devices[this._currentDeviceName].new_version_num)
                if (msg.version < this._devices[this._currentDeviceName].new_version_num){
                    this._pushBeginDeviceUpdateMsg()
                    this._updatingDevice()
                }
                else {
                    this._updateFinishRequestServer()
                    this.showOrHideLoading("",false)
                    this.showCancelOrConfirmDialog("",false)
                    this.showSuccessToast("已经是最新版本")
                }
            }
            else if (msg.type == 6){
                if (this._dialog.cancelAndConfirmDialog.css('display') == 'none' || this._dialog.cancelAndConfirmDialog.css('opacity') <= 0)
                    this._updatingDevice()
                // this._updateProgress(msg.status)
            }
            else if (msg.type == 7){
                this._updateFailed()
            }

        },
        showOrHideLoading : function (tips,letshow) {
            this._dialog.loading.find("p").html(tips)
            letshow ? this._dialog.loading.fadeIn(200) : this._dialog.loading.fadeOut(200)
        },
        showSuccessToast : function (tips) {
            this._dialog.successToast.find("p").html(tips)
            this._dialog.successToast.fadeIn(200)
            var thiz = this
            setTimeout(function () {
                thiz._dialog.successToast.fadeOut(200)
            },2000)
        },
        showFaildToast : function (tips) {
            this._dialog.faildToast.find("p").html(tips)
            this._dialog.faildToast.fadeIn(200)
            setTimeout(function () {
                this._dialog.faildToast.fadeOut(200)
            },2000)
        },
        _updatingDevice : function (value=0){
            console.log("updating device")
            this.hideDialog()
            // this.showOrHideLoading("",false)
            var dialog_obj = this._dialog.cancelAndConfirmDialog
            dialog_obj.find(".confirm-button").unbind()
            var content = dialog_obj.find(".weui-dialog__bd")
            content.html("")
            dialog_obj.find("a").hide()
            // var progress_obj = this._dialog.updateProgress.clone()
            // this._currentUpdateProgressObj = progress_obj
            // progress_obj.addClass("margin-top25")
            content.append('<i class="weui-loading"></i><br>')
            var msg = this._devices[this._currentDeviceName].nick_name + '正在升级，请勿关闭本页面，升级过程可能需要1～5分钟'
            content.append(msg)

            // dialog_obj.find(".js_progress").css("width",value+"%")
            // progress_obj.fadeIn(200)
            dialog_obj.fadeIn(200)
        },
        _updateFinishRequestServer : function () {
            this.showCancelOrConfirmDialog("",false)
            this.showOnlyConfirmDialog("恭喜！设备 " + this._devices[this._currentDeviceName].nick_name + " 升级成功")
            this._devices[this._currentDeviceName].version = this._devices[this._currentDeviceName].new_version_num
            this._devices[this._currentDeviceName].device_update = false
            console.log($("#list-"+this._currentDeviceName))
            $("#list-"+this._currentDeviceName).find(".weui-badge").hide()
            var n = $(".weui-bar__item_on").find(".weui-badge").html()
            n = parseInt(n) - 1
            if (n <= 0)
                $(".weui-bar__item_on").find(".weui-badge").hide()
            $(".weui-bar__item_on").find(".weui-badge").html(n)

            $(".device-setting").find(".weui-badge").hide()
            $("#device-update-button").hide()


            $.post("/api/device/update/",{"device_name" : this._currentDeviceName,"version" : this._devices[this._currentDeviceName].new_version_num},function (data) {
                    console.log(data)
                })
        },
        _updateProgress : function (value) {
            console.log(value)
            if (value >= 100){
                var thiz = this
                this.showCancelOrConfirmDialog("升级完成，设备将会自动重启后即可正常操作，请等待10秒",true)
                this._updateFinishRequestServer()
                setTimeout(function () {
                    thiz.hideDialog()
                    thiz.showCancelOrConfirmDialog("",false)
                },10000)

                // this.showOnlyConfirmDialog("升级完成，设备将会自动重启后即可正常操作，此过程一般需要10秒")
            }
            // else
            //     this._currentUpdateProgressObj.find(".js_progress").css("width",value+"%")
        },
        _updateFailed : function () {
            console.log("Upgrade failed")
            this.showCancelOrConfirmDialog("",false)
            this.showOnlyConfirmDialog("升级失败，请保持设备联网并稍后再次尝试升级")
        },
        _changeDeviceOnline : function(device_name) {
            console.log("Now i am change device to online")
            console.log($("#list-"+device_name))
            this._devices[device_name].onActive = true
            $("#list-"+device_name).css("opacity",1)
            $("#list-"+device_name + " input").prop('disabled', false);
            $("#list-"+device_name + " i").removeClass("weui-icon-cancel")
            $("#list-"+device_name + " i").addClass("weui-icon-success")
            $("#list-"+device_name + " span").html("在线")
            $(".switch-text").html(this._devices[device_name].status ? "灯已开" : "灯已关")
        },
        loadingDeviceSettingPage : function () {
            this.getDeviceShareCode()
            this.loadDeviceDetail()
            var thiz = this
            $("#device-update-button").click(function () {
                var dialog_obj = thiz._dialog.cancelAndConfirmDialog
                dialog_obj.find(".confirm-button").unbind()
                dialog_obj.find("a").show()
                thiz.showCancelOrConfirmDialog("点击确认开始升级设备设备，升级过程请勿断开设备电源和Wi-Fi，升级过程将会屏蔽用户的控制操作")

                dialog_obj.find(".confirm-button").click(function () {
                    console.log("Click Confirm Update")
                    thiz.showOrHideLoading("准备升级中",true)
                    thiz._pushGetDeviceVersionMsg()
                })

            })

            $('#unbinding-device-button').on('click', function(){
                thiz.showUnbindingWarning()
            });

            $("#device-ccname-button").click(function () {
                thiz.changeDeviceName()
            })

        },
        showOnlyConfirmDialog : function (tips) {
            var obj = this._dialog.confirmDialog
            obj.find(".weui-dialog__bd").html(tips)
            obj.show()
            obj.css("transform","None")
            obj.fadeIn(200)
        },
        showCancelOrConfirmDialog : function (tips,value=true) {
            var obj = this._dialog.cancelAndConfirmDialog
            obj.find(".weui-dialog__bd").html(tips)
            value ?  obj.fadeIn(200) : obj.fadeOut(200)
        },
        hideDialog : function () {
            $(".global-dialogs").fadeOut(200)

        },
        deviceUpgrade : function(){},
        loadDeviceDetail : function(){
            var device = this._devices[this._currentDeviceName]
            $("#device-nick_name").attr("placeholder",device.nick_name)
            if (device.device_update){
                $("#device-version input").val("v" + device.version + " (点击下方升级最新版本)")
                $("#device-version input").css({"font-size":"15px","color":"#07C160"})
                $("#device-update-button").show()
            }
            else {
                $("#device-version input").val("v" + device.version)
                $("#device-update-button").hide()
            }
            $("#device-dingding-date input").val(device.binding_date)
            if (device.is_share) {
                $("#device-from input").val("来自于 " + device.share_from + " 的分享")
            }
            else {
                $("#device-from input").val("设备主用户")
            }

            $.post("/api/device/bind/log/",{"device_name":this._currentDeviceName},function (data) {
                console.log(data)
                $("#device-users-list-content").html("")
                if (data.code == -1){
                    var obj_tpl = $(".binding-user-list")
                    data.data.forEach(function (user) {
                        obj = obj_tpl.clone()
                        obj.find("img").attr("src",user.user_headimg)
                        obj.find("p").html(user.user_nickname)
                        if (user.origin_nickname != null)
                            obj.children(".weui-cell__ft").html("来自" + user.origin_nickname + "的分享")
                        else
                            obj.children(".weui-cell__ft").html("设备主用户")
                        $("#device-users-list-content").append(obj)
                        obj.show()
                    })


                }
            })
        },
        getDeviceShareCode : function(){
            if (!this._devices[this._currentDeviceName].is_share){
                $("#share-qrcode-content").show()
                $(".kessk-loading").css("display","inline-block")
                $.post("/api/user/share/",{"device_id":this._currentDeviceName},function (data) {
                    console.log(data)
                    if (data.code == -1){
                        var url = data["data"]["url"]
                        console.log(url)
                        $("#share-qrcode-content img").attr("src",url)
                    }
                })

                $("#share-qrcode-content img").on("load",function(){
                    $(".kessk-loading").hide()
                });
            }
            else {
                $(".kessk-loading").hide()
                $("#share-qrcode-content").hide()
            }
        },
        unbindDevice : function(){
            this.hideDialog()
            this.showOrHideLoading("正在解绑",true)
            $.post("/api/device/unbind/",{"device_name":this._currentDeviceName},function (data) {
                this.showOrHideLoading("",false)
                if (data.code == -1){
                    this.successToast("解绑成功")
                    window.location.href = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx8dc705a03c99a21f&redirect_uri=https://airless.ngrok2.xiaomiqiu.cn/user/index/&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
                }
                else {
                    this.showFaildToast("解绑失败，请重新尝试")
                }
            })
        },
        showUnbindingWarning : function(){
            this._dialog.cancelAndConfirmDialog.find(".confirm-button").unbind()
            var thiz = this
            var device = this._devices[this._currentDeviceName]
            if (device.is_share) {
                this.showCancelOrConfirmDialog("解绑后你将无法控制该设备")
                // $("#tips-content").html("解绑后你将无法控制该设备")
            }
            else {
                this.showCancelOrConfirmDialog("解绑后你将无法控制该设备,并且你分享的用户也将无法控制该设备")
                // $("#tips-content").html("解绑后你将无法控制该设备,并且你分享的用户也将无法控制该设备")
            }

            this._dialog.cancelAndConfirmDialog.find(".confirm-button").click(function () {
                thiz.unbindDevice()
            })
        },
        changeDeviceName : function () {
            var name = $("#device-nick_name").val()
            if (name == null || name == "" || name == this._devices[this._currentDeviceName].nick_name){
                return
            }
            this.showOrHideLoading("正在更名",true)
            var thiz = this
            $.ajax({
                url: '/api/device/ccname/',
                type: 'PUT',
                data: {"chip": this._currentDeviceName, "name": name,"is_name":true},
                success: function (data) {
                    thiz._devices[thiz._currentDeviceName].nick_name = name
                    thiz.showOrHideLoading("",false)
                    thiz.showSuccessToast("更名成功")
                }

            })
        },
        changeUserIndex : function () {
            var pickerData = []
            var thiz = window.deviceController
            var this_ = this
            pickerData.push({
                label: '默认',
                value: 0,
            })
            for (key in thiz._devices){
                pickerData.push({
                    label : thiz._devices[key].nick_name,
                    value : key
                })
            }
            weui.picker(pickerData , {
                onChange: function (result) {
                    console.log(result);
                },
                onConfirm: function (result) {
                    $(".default-index-name").html(result[0].label)
                    if (result[0].value != GLOBAL_INDEX_DEVICE_NAME) {
                        $.post("/api/user/ccindex/", {"device_name": result[0].value}, function (data) {
                            if (data.code == -1)
                                window.location.href = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx8dc705a03c99a21f&redirect_uri=https://airless.ngrok2.xiaomiqiu.cn/user/index/&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect';
                        })
                    }
                },
                title: '选择默认首页'
            });
        },
        checkDeviceListStatus : function () {
            for (key in this._devices) {
                if (this._devices[key].onActive){
                    this._changeDeviceOnline(key)
                    var switchObj = $("#list-"+key + " input")
                    var switchObjTips = $("#list-"+key + " .switch-label")
                    switchObj.prop("checked",this._devices[key].status)
                    switchObjTips.html(this._devices[key].status ? "开" : "关")
                }

            }
        },
        setCurrentDeviceName : function(device_name) {
            this._currentDeviceName = device_name
        },
        getCurrentDeviceNickName : function() {
          return this._devices[this._currentDeviceName].nick_name
        },
        getSholdUpdate : function () {
            return this._devices[this._currentDeviceName].device_update
        },
        getDeviceOnlineStatus : function () {
            return this._devices[this._currentDeviceName].onActive
        },
        clearDialog : function(){},
        getDevice : function(){},



        ftest: function () {
            console.log(this._tt)
        }
    }

    function init(){
        fastClick();
        console.log(665)
        androidInputBugFix();
        console.log(667)
        setPageManager();
        console.log(669)
        console.log("I am init now")
        window.pageManager = pageManager;
        window.deviceController = deviceController;
        window.home = function(){
            location.hash = '';
        };
    }
    init();



    $('.js_dialog').on('click', '.cancel-button', function(){
        $(this).parents('.js_dialog').fadeOut(200);
    });



    // GLOBAL_CONTROL_DEVICE.on('connect', () => {
    //     console.log("Connect Success")
    //     $("#loadingToast").hide()
    //     get_devices_status()
    // })
    //
    // GLOBAL_CONTROL_DEVICE.on('message', (topic, payload) => {
    //    handle_device_status(topic,payload)
    // });

    // function handle_device_status(topic,payload){
    //     message_json = JSON.parse(payload.toString())
    //     turn_device(message_json.device,message_json.status)
    //     if (message_json.type==0 && CURRENT_DEVICE_NAME == message_json.device){
    //         change_status()
    //     }
    // }

    // function turn_device(device_name,value) {
    //     var obj = $("#list-"+device_name + " input")
    //     var lobj = $("#list-"+device_name + " .switch-label")
    //     obj.prop("checked",value)
    //     value ? lobj.html("开") : lobj.html("关")
    //     GLOBAL_DEVICES[device_name].status = value
    // }
    //
    // function switch_device(device_name) {
    //     turn_device(device_name,!GLOBAL_DEVICES[device_name].status)
    //     var msg = '{"type":0,"status":'+ GLOBAL_DEVICES[device_name].status +',"control_device":"no","deviceName":"'+ device_name +'"}'
    //     GLOBAL_CONTROL_DEVICE.publish(GLOBAL_CONTROL_DEVICE_TOPIC_UPDATE,msg)
    // }





})