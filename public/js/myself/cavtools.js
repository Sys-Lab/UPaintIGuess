var MyCanvas = {
	x:null,
	y:null,
	canvas:null,
	Context2D:null,
	init:function(canvas,Context2D){
		this.x = [];//记录鼠标移动是的X坐标
		this.y = [];//记录鼠标移动是的Y坐标
		//this.clickDrag=[];
		this.eraserRadius=15;//擦除半径值
		this.canvas = canvas;
		this.Context2D = Context2D;
		this.Context2D.lineJoin = "round";//context.lineJoin - 指定两条线段的连接方式
        this.Context2D.lineWidth = 5;//线条的宽度
		this.w=this.canvas.width;//取画布的宽
		this.h=this.canvas.height;//取画布的高 
	},
	movePoint:function(x,y,dragging){
		this.x.push(x);
        this.y.push(y);
        //this.clickDrag.push(dragging);
	},
	drawPoint:function(){
		for(var i=0; i < this.x.length; i++)//循环数组
		{
			this.Context2D.beginPath();//context.beginPath() , 准备绘制一条路径
			
			if(this.x[i] && i){//当是拖动而且i!=0时，从上一个点开始画线。
				this.Context2D.moveTo(this.x[i-1], this.y[i-1]);//context.moveTo(x, y) , 新开一个路径，并指定路径的起点
			}else{
				this.Context2D.moveTo(this.x[i]-1, this.y[i]);
			}
			this.Context2D.lineTo(this.x[i], this.y[i]);//context.lineTo(x, y) , 将当前点与指定的点用一条笔直的路径连接起来
			this.Context2D.closePath();//context.closePath() , 如果当前路径是打开的则关闭它
			this.Context2D.stroke();//context.stroke() , 绘制当前路径
		}
	},
	drawPath:function(_x,_y){
		for(var i=0; i < _x.length; i++)//循环数组
		{   
			this.Context2D.beginPath();//context.beginPath() , 准备绘制一条路径
			
			if(_x[i] && i){//当是拖动而且i!=0时，从上一个点开始画线。
				this.Context2D.moveTo(_x[i-1], _y[i-1]);//context.moveTo(x, y) , 新开一个路径，并指定路径的起点
			}else{
				this.Context2D.moveTo(_x[i]-1, _y[i]);
			}
			this.Context2D.lineTo(_x[i], _y[i]);//context.lineTo(x, y) , 将当前点与指定的点用一条笔直的路径连接起来
			this.Context2D.closePath();//context.closePath() , 如果当前路径是打开的则关闭它
			this.Context2D.stroke();//context.stroke() , 绘制当前路径
		}
	
	},
	pen_Size:function(size){
		this.Context2D.lineWidth = size;
	},
	pen_Color:function(color){
		this.Context2D.strokeStyle = color;
	},
	canvasClear:function(){
		this.Context2D.clearRect(0, 0, this.w, this.h);//清除画布，左上角为起点
	},
	eraser:function(_x,_y){
		this.Context2D.globalCompositeOperation = "destination-out";
		this.Context2D.beginPath();
		this.Context2D.arc(_x, _y, this.eraserRadius, 0, Math.PI * 2);
		this.Context2D.strokeStyle = "rgba(250,250,250,0)";
		this.Context2D.fill();
		this.Context2D.globalCompositeOperation = "source-over"
	},
	eraserPath:function(_x,_y){
		this.Context2D.globalCompositeOperation = "destination-out";
		for(var i=0; i < _x.length; i++){
			this.Context2D.beginPath();
			this.Context2D.arc(_x[i], _y[i], this.eraserRadius, 0, Math.PI * 2);
			this.Context2D.strokeStyle = "rgba(250,250,250,0)";
			this.Context2D.fill();
		}
		this.Context2D.globalCompositeOperation = "source-over"
	},
	getUrl:function(){
		open(this.canvas.toDataURL());//弹出新窗口显示画的图片
	},

}