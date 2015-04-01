/*
    *使用时先初始化paint.init(),再决定显示或者不显示tools   paint.toolsVisible() OR paint.toolsUnvisible()
    *主要外部调用方法：init()，toolsVisible()，toolsUnvisible()，eraser_Path(_x,_y)，pen_Path(_x,_y)，getUrl()，canvasClear()，pen_Size(size)，pen_Color(color)，setQuestion(question)，
*/
var paint = {
    init: function() {
        this.canvas = this.$("canvas");
        if(this.canvas.getContext) {} else {
            alert("您的浏览器不支持 canvas 标签");
            return;
        }
        this.Context2D = this.canvas.getContext('2d');
        this.x = [];//记录鼠标移动是的X坐标
        this.y = [];//记录鼠标移动是的Y坐标
        this.eraserRadius=15;//擦除半径值
        this.Context2D.lineJoin = "round";//context.lineJoin - 指定两条线段的连接方式
        this.Context2D.lineWidth = 5;//线条的宽度
        this.w=this.canvas.width;//取画布的宽
        this.h=this.canvas.height;//取画布的高
        this.touch = ("createTouch" in document); //判定是否为手持设备
        this.StartEvent = this.touch ? "touchstart" : "mousedown"; //支持触摸式使用相应的事件替代
        this.MoveEvent = this.touch ? "touchmove" : "mousemove";
        this.EndEvent = this.touch ? "touchend" : "mouseup";
        this.tools = this.$("top");//顶部工具div
        this.quesDiv = this.$("quesDiv");//显示题目的div
    },
    $: function(id) //判断参数id的类型，并返回相应对象
    {
        return typeof id == "string" ? document.getElementById(id) : id;
    },
    load: function() {
        this.lock = false; //鼠标移动前，判断鼠标是否按下
        this.isEraser = false;
        this.storageColor = "#000000";
        this.color = ["#000000", "#FF0000", "#80FF00", "#00FFFF", "#808080", "#FF8000", "#408080", "#8000FF", "#CCCC00"]; //画笔颜色值
        this.fontWeight = [5, 10, 15];

        this.iptClear = this.$("clear"); //清除画布按钮
        this.question = this.$("question");//题目提示框
        this.addcolor = this.$("addcolor");
        this.imgurl = this.$("imgurl"); //导出图片路径按钮
    },
    //start 以下两个方法是辅助获取鼠标在画布上的坐标位置
    getOffset:function(evt){
        var target = evt.target;
        if (target.offsetLeft == undefined){
            target = target.parentNode;
        }
        var pageCoord = this.getPageCoord(target);
        var eventCoord ={
                        x: window.pageXOffset + evt.clientX,
                        y: window.pageYOffset + evt.clientY
        };
        var offset ={
                    offsetX: eventCoord.x - pageCoord.x,
                    offsetY: eventCoord.y - pageCoord.y
        };
        return offset;
    },
    getPageCoord:function(element){
        var coord = {x: 0, y: 0};
        while (element){
            coord.x += element.offsetLeft;
            coord.y += element.offsetTop;
            element = element.offsetParent;
        }
        return coord;
    },
    //end
    bind: function() {
        var t = this; /*清除画布*/
        this.canvas.style.cursor = "url(../../Tpl/public/img/b.cur) 4 31, auto";//设置鼠标为画笔样式
        this.iptClear.onclick = function() {
            t.canvasClear();
            websocket.send_Clear();
        }; /*鼠标按下事件，记录鼠标位置，并绘制，解锁lock，打开mousemove事件*/
        this.canvas['on' + t.StartEvent] = function(e) {
            var touch = t.touch ? e.touches[0] : e;

            var _x = t.getOffset(touch).offsetX ;//鼠标在画布上的x坐标，以画布左上角为起点
            var _y = t.getOffset(touch).offsetY;//鼠标在画布上的y坐标，以画布左上角为起点
            // var _x = (touch.offsetX==undefined) ? t.getOffset(touch).offsetX : touch.offsetX ;//鼠标在画布上的x坐标，以画布左上角为起点
            // var _y = (touch.offsetY==undefined) ? t.getOffset(touch).offsetY : touch.offsetY ;//鼠标在画布上的y坐标，以画布左上角为起点
            if(t.isEraser) {
                t.movePoint(_x, _y); //记录鼠标位置
                t.eraser(_x, _y);
            } else {
                t.movePoint(_x, _y); //记录鼠标位置
                t.drawPoint(); //绘制路线
            }
            t.lock = true;
            return false; //阻止chrome移动过程中默认鼠标样式
        }; /*鼠标移动事件*/
        this.canvas['on' + t.MoveEvent] = function(e) {
            var touch = t.touch ? e.touches[0] : e;
            if(t.lock) //t.lock为true则执行
            {
                var _x = t.getOffset(touch).offsetX ;//鼠标在画布上的x坐标，以画布左上角为起点
                var _y = t.getOffset(touch).offsetY;//鼠标在画布上的y坐标，以画布左上角为起点
                // var _x = (touch.offsetX==undefined) ? t.getOffset(touch).offsetX : touch.offsetX ;//鼠标在画布上的x坐标，以画布左上角为起点
                // var _y = (touch.offsetY==undefined) ? t.getOffset(touch).offsetY : touch.offsetY ;//鼠标在画布上的y坐标，以画布左上角为起点
                if(t.isEraser) {
                    t.movePoint(_x, _y); //记录鼠标位置
                    t.eraser(_x, _y);
                } else {
                    t.movePoint(_x, _y); //记录鼠标位置
                    t.drawPoint(); //绘制路线
                }
            }
        };
        //鼠标单击后释放时间
        this.canvas['on' + t.EndEvent] = function(e) { /*重置数据*/
            t.lock = false;
            t.serverPush();
            t.x = [];
            t.y = [];
        };
        this.changeColor();
        //获取图片
        this.imgurl.onclick = function() {t.getUrl();};
        /*橡皮擦*/
        this.$("eraser").onclick = function(e) {
            t.isEraser = true;
            t.canvas.style.cursor = "url(../../Tpl/public/img/x.cur) 6 15, auto";
            t.$("eraser").className = "grea";
        };
    },
    //add start
    //设置顶端工具栏可见
    toolsVisible:function(){
        this.tools.style.visibility="visible";
        this.quesDiv.style.visibility="visible";
        // this.tools.innerHTML = [
        //                             '<div id="color">',
        //                                 'Brush Color：',
        //                                 '<input class="i1" type="button" value="" />',
        //                                 '<input class="i2" type="button" value="" />',
        //                                 '<input class="i3" type="button" value="" />',
        //                                 '<input class="i4" type="button" value="" />',
        //                                 '<input class="i5" type="button" value="" />',
        //                                 '<input class="i6" type="button" value="" />',
        //                                 '<input class="i7" type="button" value="" />',
        //                                 '<input class="i8" type="button" value="" />',
        //                                 '<input class="i9" type="button" value="" />',
        //                             '</div>',
        //                             '<div class="font" id="font">',
        //                                 'Brush Width：',
        //                                 '<input type="button" value="thin" class="grea"/>',
        //                                 '<input type="button" value="medium" />',
        //                                 '<input type="button" value="thick" />',
        //                             '</div>',
        //                             '<div>',
        //                                 '<span id="error">Eraser：</span>',
        //                                 '<input id="eraser" style="width:60px;font-size:14px;"type="button" value=""/>',
        //                             '</div>',
        //                             '<input id="clear" type="button"  style="width:80px;"/>',
        //                            
        //                         ].join("");
        // this.quesDiv.innerHTML = [
        //                         '<div id="quesDiv">',
        //                         '    Your Current Title：<input class="tishi" id="question" type="button" value="火车">',
        //                         '</div>'
        //                         ].join("");
                                this.load();
                                this.addColor();
                                this.bind();
                                
    },
    //设置顶端工具栏不可见
    toolsUnvisible:function(){
        this.tools.style.visibility="hidden";
        this.quesDiv.style.visibility="hidden";


        // this.tools.innerHTML = "";
        // this.quesDiv.innerHTML = "";

        this.canvas.style.cursor = "auto";
        this.canvas['on' + this.StartEvent] = function(e) {}; //鼠标点击
        this.canvas['on' + this.MoveEvent] = function(e) {};//鼠标移动事件
        this.canvas['on' + this.EndEvent] = function(e) {};//鼠标单击后释放时间
    },
    //本地橡皮擦调用方法
    eraser:function(_x,_y){
        this.Context2D.globalCompositeOperation = "destination-out";
        this.Context2D.beginPath();
        this.Context2D.arc(_x, _y, this.eraserRadius, 0, Math.PI * 2);
        this.Context2D.strokeStyle = "rgba(250,250,250,0)";
        this.Context2D.fill();
        this.Context2D.globalCompositeOperation = "source-over";
    },
    //根据给定路径绘制橡皮擦的轨迹
    eraser_Path:function(_x,_y){
        this.Context2D.globalCompositeOperation = "destination-out";
        for(var i=0; i < _x.length; i++){
            this.Context2D.beginPath();
            this.Context2D.arc(_x[i], _y[i], this.eraserRadius, 0, Math.PI * 2);
            this.Context2D.strokeStyle = "rgba(250,250,250,0)";
            this.Context2D.fill();
        }
        this.Context2D.globalCompositeOperation = "source-over";
    },
    movePoint:function(x,y,dragging){
        this.x.push(x);
        this.y.push(y);
    },
    //划线的方法，用于本地
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
    //根据给定的path路径绘制线条，
    pen_Path:function(_x,_y){
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
    //获取图片的url
    getUrl:function(){
        open(this.canvas.toDataURL());//弹出新窗口显示画的图片
    },
    //清除画布
    canvasClear:function(){
        this.Context2D.clearRect(0, 0, this.w, this.h);//清除画布，左上角为起点
    },
    //改变画笔粗细
    pen_Size:function(size){
        this.Context2D.lineWidth = size;
    },
    //改变画笔颜色
    pen_Color:function(color){
        this.Context2D.strokeStyle = color;
    },
    //end
    //设置题目的内容
    setQuestion:function(question){
        this.question.value = question;
    },
    preventDefault: function(e) { /*阻止默认*/
        var touch = this.touch ? e.touches[0] : e;
        if(this.touch) touch.preventDefault();
        else window.event.returnValue = false;
    },
    changeColor: function() { /*为按钮添加事件*/
        var t = this,
        iptNum = this.addcolor.getElementsByTagName("input"),
        fontIptNum = this.$("font").getElementsByTagName("input");
        for(var i = 0, l = iptNum.length; i < l; i++) {
            iptNum[i].index = i;
            iptNum[i].onclick = function() {
                t.changeColorBackground(this.index);
                t.Context2D.strokeStyle = t.color[this.index];
                t.storageColor = t.color[this.index];
                t.canvas.style.cursor = "url(../../Tpl/public/img/b.cur) 4 31, auto";
                t.isEraser = false;
                t.$("eraser").className = "";
            };
        }
        for(var i = 0, l = fontIptNum.length; i < l; i++) {
            fontIptNum[i].index = i;
            fontIptNum[i].onclick = function() {
                t.changeBackground(this.index);
                t.Context2D.lineWidth = t.fontWeight[this.index];
                t.canvas.style.cursor = "url(../../Tpl/public/img/b.cur) 4 31, auto";
                t.isEraser = false;
                t.$("eraser").className = "";
                t.Context2D.strokeStyle = t.storageColor;
            };
        }
    },
    //设置选中的画笔粗细的外观
    changeBackground: function(num) { /*添加画笔粗细的提示背景颜色切换，灰色为当前*/
        var fontIptNum = this.$("font").getElementsByTagName("input");
        for(var j = 0, m = fontIptNum.length; j < m; j++) {
            fontIptNum[j].className = "";
            if(j == num) fontIptNum[j].className = "grea";
        }
    },
    //设置选中的颜色外观
    changeColorBackground:function(num){
        var color = this.addcolor.getElementsByTagName("input");
        for(var j=0,m = color.length; j < m; j++){
            color[j].className = "";
            if(j == num) color[j].className = "on";
        }

    },
    //为addcolor标签内添加画笔颜色，颜色为color给定的
    addColor:function(){
        var addUlHtml = ["Brush Color："];
        for (var i = 0, l = this.color.length; i < l; i++) {
            addUlHtml.push('<input style="background: ' + this.color[i] + '" type="button" value="" class="' + (i == 0 ? "on" : "") + '"/>');
        }
        this.addcolor.innerHTML = addUlHtml.join("");
    },
    //用于调用websocket，发送用户的相关操作
    serverPush: function() {
        var pathX = this.x.toString();
        var pathY = this.y.toString();
        if(this.isEraser) {
            websocket.send_Eraser(pathX, pathY);
        } else {
            var color = this.Context2D.strokeStyle.toString();
            var size = this.Context2D.lineWidth.toString();
            websocket.send_Pen(pathX, pathY, color, size);
        }
    }
};