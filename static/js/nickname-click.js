function fadeOut(el){
    el.style.opaticy = 1;

    (function fade(){
        if ( (el.style.opacity -= 0.1 ) < 0 ){
            $(el).removeClass("display-block");
        }
        else {
            requestAnimationFrame(fade);
        }
    })();
}

function fadeIn(el){
    el.style.opacity = 0;
    $(el).addClass("display-block");

    (function fade() {
        var val = parseFloat(el.style.opacity);
        if (!((val += 0.1) > 1)) {
            el.style.opacity = val;
            requestAnimationFrame(fade);
        }
    })();
}

$(document).ready(function(){
    var nicknames = document.getElementsByClassName('nickname-click');
    for ( var i = 0 ; i < nicknames.length; i++ ) {
        var nick = nicknames[i];
        var nickname = nick.textContent;
        nick.innerHTML = nickname + "<div class='nickname-link'><ul><li><a href='../all/?nickname=" + nickname + "' >작성 글 보기</a></li><li><a href='" + 'javascript:popupOpen("' + nickname + '");' + "'>쪽지 보내기</a></li></ul></div>";
    }

    $('.nickname-click').click(function(){
        if ( $(this.getElementsByClassName("nickname-link")[0]).hasClass("display-block")){
            fadeOut(this.getElementsByClassName("nickname-link")[0]);
        }
		else{
            var elements = document.getElementsByClassName('nickname-click');
            for ( var i = 0; i < elements.length; i++ ) {
                var td = elements[i]
                if ( $(td.getElementsByClassName("nickname-link")[0]).hasClass("display-block") && td!==this){
                    fadeOut(td.getElementsByClassName("nickname-link")[0]);
                };
            };

           fadeIn(this.getElementsByClassName("nickname-link")[0]);
        }
    });
});

function popupOpen(recipient){
    var popUrl = "/board/send_message/?to=" + recipient;
    var popOption = "width = 370, height = 360, location = no, menubar = no, scrollbars = no, status = no, toolbar = no, left = 400, top = 200;";
    window.open(popUrl, "쪽지 보내기",  popOption);
}
