/*
	*使用：聊天框的相关方法
*/
var chat = {
	color:"black",
	$: function(id) {
		return document.getElementById(id);
	},
	log: function(msg) {//log(msg)把msg显示到聊天窗口；
		var t = this;
		t.$("log").innerHTML += "<br>" + "<font color=" + this.color + ">" + msg + "</font>";
		this.color = "black";
		//设置滚动条位于文本末尾
		var obj = $("log");
		obj.scrollTop = obj.scrollHeight;
	},
	onkey: function(event) {//enter键的监听
		if(event.keyCode == 13) {
			roomnum = "1";
			this.send_Msg();
			// name = "pljhognlu";
			// msg = this.getInputMsg();
			// websocket.send_Msg(roomnum,name,msg);
		}
	},
	send_Msg:function(){//发送按钮的监听，应该加入
		//TODO 这里应该加入判断发送的msg是不是正确答案的代码

		roomnum = "1";
		name = "pljhognlu";
		msg = this.getInputMsg();
		if(!msg.trim()) {
			alert("Message can not be empty");
			return;
		}
		websocket.send_Msg(roomnum,name,msg);
	},
	getInputMsg:function(){//得到用户输入框的文本内容
		var txt, msg;
		txt = this.$("msg");
		msg = txt.value;
		txt.value = "";
		txt.focus();
		return msg;
	},
	setMsgColor:function(color){
		this.color = color;
	}
}