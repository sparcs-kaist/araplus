$(document).ready(function(){
	$('.nickname_td').click(function(){
		$(this.getElementsByTagName("span")[0]).toggleClass('nickname_td-toggle');
		$(this.getElementsByClassName("nickname-link")[0]).toggleClass('nickname-link-toggle');
		
		var elements = document.getElementsByClassName('nickname_td');
		for ( var i = 0; i < elements.length; i++ ) {
			var td = elements[i]
			if ( $(td.getElementsByTagName("span")[0]).hasClass("nickname_td-toggle") && td!==this){
				$(td.getElementsByTagName("span")[0]).removeClass('nickname_td-toggle');
				$(td.getElementsByClassName("nickname-link")[0]).removeClass('nickname-link-toggle');
			};
		};
	});

	
});
function popupOpen(recipient){
	var popUrl = "/board/send_message/?to=" + recipient;
	var popOption = "width = 370, height = 360, location = no, menubar = no, scrollbars = no, status = no, toolbar = no, left = 400, top = 200;";
	window.open(popUrl, "쪽지 보내기",  popOption);
}
