var timer = {
	_init:function(){
		this.max = 62;
		this._now = 0;
		this._timeDiv_id = "countdown";
		this._timeDiv = document.getElementById(this._timeDiv_id);
		clearInterval(this._timeout);
	},
	_setTime:function(time){
		this._timeDiv.innerHTML = time;
	},
	timerStart:function(){
		this._init();
		var t = this;
		t._now = t.max;
		this._timeout = setInterval(function(){
			if(t._now >= 0){
				t._setTime(t._now--);
			}else{
				t._timeOver();
				return;
			}
		},1000);
	},
	_timeOver:function(){
		clearInterval(this._timeout);
		chat.log('draw time out!');
		paint.toolsUnvisible();
		this.answer_timerStart();
	},
	answer_timerStart:function(){
		this._init();
		var t = this;
		t._now = 30;
		this._timeout = setInterval(function(){
			if(t._now >= 0){
				t._setTime(t._now--);
			}else{
				t._answer_timeOver();
				return;
			}
		},1000);
	},
	_answer_timeOver:function(){
		clearInterval(this._timeout);
		chat.log('answer time out!');
		websocket.end_game();
		paint.toolsUnvisible();
	}
}
