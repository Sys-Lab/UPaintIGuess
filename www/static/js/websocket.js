var websocket={
	init:function(){
		var t=this;
		t.room='1'
		var host='http://'+window.location.host;
		try{
			t.socket=io.connect(host);
		} catch(e){
			alert(e);
		}
		t.socket.on('connect',function(){
			t.socket.on('draw',function(data){
				if(data.point.type=="eraser"){
					paint.eraser_Path(data.point.x.split(","), data.point.y.split(","));
				}
				else{
					paint.pen_Size(data.point.size);
					paint.pen_Color(data.point.color);
					paint.pen_Path(data.point.x.split(","), data.point.y.split(","));
				}
			});
			t.socket.on('msg',function(data){
				chat.log(data);
			});
			t.socket.on('ready',function(data){
				paint.toolsUnvisible();
				$('.top').hide();
				timer.timerStart();
			});
			t.socket.on('word',function(data){
				chat.log(data);
				paint.toolsVisible();
				$('.top').show();
			});
			t.socket.on('restart',function(data){
				$('#ready').show();
				paint.canvasClear();
			});
			t.socket.on('join',function(data){
				setroom(data);
			});
			t.socket.on('clear',function(data){
				console.log('claer')
				paint.canvasClear();
			})
		});
	},
	join:function(){
		this.socket.emit('join',{});
	},
	leave:function(){
		this.socket.emit('leave',{'room':this.room});
		this.room=null;
	},
	send_ready:function(){
		this.socket.emit('ready',{'room':this.room});
		$('#ready').hide();
		$('.send').show();
	},
	get_desc:function(){
		this.socket.emit('get_desc');
	},
	get_word:function(){
		this.socket.emit('get_word');
	},
	send_Msg:function(msg){
		this.socket.emit('msg',{'room':this.room,'message':msg});
	},
	end_game:function(){
		this.socket.emit('end',{'room':this.room});
		$('.send').hide();
	},
	send_Pen:function(pathX,pathY,colors,boldness){
		var data={
			point:
			{
				'x':pathX,
				'y':pathY,
				'color':colors,
				'size':boldness,
				'type':'pen'
			},
			'room':this.room,
		}
		this.socket.emit('draw',data);
	},
	send_Eraser:function(pathX,pathY){
		var data={
			point:
			{
				'x':pathX,
				'y':pathY,
				'color':null,
				'size':null,
				'type':'eraser'
			},
			'room':this.room
		}
		this.socket.emit('draw',data)
	},
	send_Clear:function(){
		this.socket.emit('clear',{'room':this.room});
	}
	
}

function setroom(data){
	websocket.room=data;
}