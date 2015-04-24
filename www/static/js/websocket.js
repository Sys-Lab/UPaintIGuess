// Current User ID allocated by server for identification
var current_id = '';

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
				if(data.type=="eraser"){
					paint.eraser_Path(data.x.split(','), data.y.split(','));
				}
				else{
					paint.pen_Size(data.size);
					paint.pen_Color(data.color);
					paint.pen_Path(data.x.split(','), data.y.split(','));
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
				if(current_id == data.user){
					paint.toolsVisible();
					chat.log(data.word);
					$('.top').show();
				} else {
					paint.toolsUnvisible();
					$('.top').hide();
				}
			});
			t.socket.on('restart',function(data){
				$('#ready').show();
				paint.canvasClear();
			});
			t.socket.on('join',function(data){
				setroom(data);
			});
			t.socket.on('user_answer_ok',function(data){
				if(data == current_id){
					paint.toolsUnvisible();
				}
				$('.top').hide();
			});
			t.socket.on('end_this_session', function(data){
				location.assign('/room', '');
			});
			t.socket.on('user', function(data) {
				//current_id = data;
			});
			t.socket.on('clear',function(data){
				console.log('clear')
				paint.canvasClear();
			})
		});
	},
	join:function(){
		current_id = $.md5((new Date().getTime()).toString() + Math.random().toString())
		this.socket.emit('join',{'user': current_id});
	},
	leave:function(){
		this.socket.emit('leave',{'room': this.room});
		this.room=null;
		location.assign('/room');
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