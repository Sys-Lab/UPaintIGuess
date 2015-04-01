var websocket = {
	init: function() {
		var t = this;
		var host = "ws://127.0.0.1:12345/thinkphp/Lib/Action/server.php";
		try {
			this.socket = new WebSocket(host);
			this.socket.onopen = function(msg) {
				//chat.log("Welcome - status " + this.readyState);
				chat.setMsgColor("red");
				chat.log("欢迎来到《你画我猜》");
			};
			this.socket.onmessage = function(msg) {
				t.Sort(msg.data);
			};
			this.socket.onclose = function(msg) {
				chat.setMsgColor("red");
				chat.log("WebSocket已关闭。");
				chat.setMsgColor("red");
				chat.log("Disconnected-status = " + this.readyState);
			};
		} catch(e) {
			chat.log(e);
		}
	},
	quit: function() {
		chat.log("Goodbye!");
		this.socket.close();
		this.socket = null;
	},
	//对从服务端socket获取的信息进行分拣，发送到不同的控件上
	Sort: function(msg) {
		//chat.log(msg);
		var thisMsg = eval('(' + msg + ')');
		if(thisMsg.type == "chat") {
			chat.log(thisMsg.name + ": " + thisMsg.msg);
// paint.toolsVisible();
timer.timerStart();
		} else if(thisMsg.type == "pen") {
			paint.pen_Size(thisMsg.size);
			paint.pen_Color(thisMsg.color);
			//.split(",")是把传过来的路径字符串转化成数组
// chat.log(thisMsg.pathx.split(","));
			paint.pen_Path(thisMsg.pathx.split(","), thisMsg.pathy.split(","));
		} else if(thisMsg.type == "eraser") {
			paint.eraser_Path(thisMsg.pathx.split(","), thisMsg.pathy.split(","));
		} else if(thisMsg.type == "clear") {
// paint.toolsUnvisible();
			paint.canvasClear();
		} else {
			chat.log("格式不正确：" + msg);
		}
	},
	//以下send*方法是为了对socket发送的数据进行包装。
	send_Msg: function(roomnum,name,msg) {
		var t = this;
		var data = {
			type: "chat",
			roomnum: roomnum,
			name: name,
			msg: msg
		};
		this.send(data);
	},
	send_Pen: function(path_x, path_y, color, size) {
		var t = this;
		var data = {
			type: "pen",
			pathx: path_x,
			pathy: path_y,
			color: color,
			size: size
		};

		this.send(data);
	},
	send_Eraser: function(path_x, path_y) {
		var t = this;
		var data = {
			type: "eraser",
			pathx: path_x,
			pathy: path_y
		};
		this.send(data);
	},
	send_Clear: function() {
		var t = this;
		var data = {
			type: "clear"
		};
		this.send(data);
	},
	send:function(array){
		var t = this;
		var msg = JSON.stringify(array);
		try {
			t.socket.send(msg);
		} catch(ex) {
			t.log("send error: " + ex);
		}
	}
};