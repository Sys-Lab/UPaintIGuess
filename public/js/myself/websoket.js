var websocket={
	init:function(){
		var t=this;
		t.room=null;
		var host='http://127.0.0.1:5000';
		try{
			t.socket=io(host);
		} catch(e){
			alert(e);
		}
		if(t.socket){
			t.socket.on('draw',function(data){
				if(data.point.type=="eraser"){
					paint.eraser_Path(data.point.x.split(","), data.point.y.split(","));
				}
				else{
					paint.pen_Size(data.point.size);
					paint.pen_Color(data.point.color);
					paint.pen_Path(data.point.x.split(","), data.point.y.split(","));
				}
			})
			t.socket.on('message',function(data){
				chat.log(data);
			})
			t.socket.on('ready',function(){
				paint.toolsUnvisible()
			})
			t.socket.on('word',function(data){
				chat.log(data);
				paint.toolsVisible();
			})
		}
	},
	join_room:function(){
		this.socket.emit('join',{'room':this.room});
	},
	leave_room:function(){
		this.socket.emit('leave',{'room':this.room});
		this.room=null;
	},
	ready:function(){
		this.socket.emit('ready',{'room':this.room});
	},
	get_desc:function(){
		this.socket.emit('get_desc');
	},
	get_word:function(){
		this.socket.emit('get_word');
	},
	send_Msg:function(msg){
		this.socket.send('msg',{'room':this.room,'message':msg});
	},
	end_game:function(){
		this.socket.emit('end',{'room':this.room});
	},
	send_Pen:function(pathX,pathY,colors,boldness){
		var data={
			point:
			{
				'x':pathX,
				'y':pathY,
				'color':colors,
				'size':boldness,
				'type':'pen',
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
				'type':'eraser',
			},
			'room':this.room
		}
		this.socket.emit('draw',data)
	},
}