$(document).ready(function(){
	current = 1;//初试移到张数
	var image_all = document.querySelectorAll(".image_each");
	var images = image_all.length;//获取改class图片张数
	width = 240;//移到一张的距离
	 var n=4;//当前显示张数

	for(i=1;i<=n;i++){
		$(image_all[i-1]).animate({"left":+(width*(i-1))+"px"},400,"swing");
	}

	$("#next").click(function(){
		current++
		if(current>=(images-n+2)){
			current=images-n+2;
		    document.div.onclick=function(){return false;}
		}
		animateLeft(current, n)		
	});
	
	$("#previous").click(function(){	
		current--
		if(current == 0){
			current=1
		document.div.onclick=function(){return false;}
		}
		animateRight(current, n)				
	});
	//向左移到next
	function animateLeft(current, n){
		//$('#p' + current).css("left", width + "px");
		$(image_all[current-2]).animate({"left": -width + "px"},400,"swing");//移除当前第一个
		
		for(i=1;i<=n;i++){
			$(image_all[current+i-2]).animate({"left":+(width*(i-1))+"px"},400,"swing");
		}	
		setbutton()
	}
	//向右移到
	function animateRight(current, n) {				
			
		$(image_all[current+n-1]).animate({"left": +(width*n) + "px"},400,"swing");//移除第二个 
		for(i=1;i<=n;i++){
			$(image_all[current+i-2]).animate({"left":+(width*(i-1))+"px"},400,"swing");
		}		        		       
		setbutton()
	}	
	function setbutton(){
		
		$('#image_each' + current).children("image_each").removeClass("current");
		$('#image_each' + current).children("image_each").addClass("current");	
	}

});