var question = {
	_init:function(){
		this._question = $("#question");
	},
	setQuestion:function(){
		var t = this;
		this._init();
		$.get("getQuestion", { roomnum: "456321" },
		function(data){
			t._question.val(data);
		});
	}
}