var refresh_timer;

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};    

var add_comment = function(grill_id){
        var form_content = $("#new_content").val()
        $("#new_content").val('');
        $.ajax({
            type: 'POST',
            url: '/grill/'+grill_id+'/add_comment/',
            data: { new_content : form_content,
                },
            dataType: 'json',
            success: function(json){
                console.log("debug")
                clearInterval(refresh_timer);
                refresh_comment(grill_id);
                refresh_timer = setInterval(function(){
                    console.log("auto");refresh_comment(grill_id);},5000);
            },
            error:function(request,status,error){
            console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);}
        });
        return false;
    };

function refresh_comment (grill_id) {
    var current_index = 0
    if ($($("#result_list>li")[0]).attr("id") != null)
    {
        current_index = $($("#result_list>li")[0]).attr("id").split("_")[1];
    }
    $.ajax({
        type: 'POST',
        url: '/grill/' + grill_id + '/refresh_comment/',
        data: {
            required_index: current_index*1+1,
        },
        dataType: 'json',
        success: function(json){
            if (json.comments.length==0)
                {
                    return false;
                };
            for (var i = json.comments.length - 1; i >= 0; i--) {
                var target = json.comments[i];
                var options = {
                    year: "numeric", month: "short",
                    day: "numeric", hour: "2-digit", minute: "2-digit"
                };
                var temp_date = new Date(target.created_time);
                var ms = '<li id="comment_'+target.order+'">' + target.order +"번째. "+target.author;
                ms += "님이 " + temp_date.toLocaleTimeString("ko-KR",options);
                ms += "에 남긴 글 <p>" + target.content + "</p></li>";
                $("#result_list").prepend(ms);   
            };
        }, error:function(request,status,error){
            console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);}
    });
}

$(document).ready(function(){
            var csrftoken = getCookie('csrftoken');
            var grill_id = document.URL.split("/")[4];
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            refresh_timer = setInterval(function(){refresh_comment(grill_id);},5000);

            $("#comment_form").on('submit',function(event){
                event.preventDefault();
                add_comment(grill_id);
            });           
            
        });
