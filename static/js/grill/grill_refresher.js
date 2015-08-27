var last_update = new Date().toJSON();

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



function refresh_comment (grill_id) {
    var current_index = 0
    if ($($("#comment-content-list>li")[0]).attr("id") != null)
    {
        current_index = $($("#comment-content-list>li")[0]).attr("id").split("-")[1];
    }
    $.ajax({
        type: 'POST',
        url: '/grill/'+grill_id +'/refresh_comment/',
        data: {
            required_index: current_index*1+1,
            last_update: last_update,
        },
        dataType: 'json',
        success: function(json){
            //Update Votes
            last_update = json.last_update
            if (!json.new_votes) {
                return false;
            };
            for (var i = json.new_votes.length - 1; i >= 0; i--) {
                var target = json.new_votes[i]
                var target_order = target.grill_comment
                var target_new_like = target.new_count
                var target_button = $($("#comment-"+target_order).find("button")[0])
                target_new_like += target_button.text().trim().split('+')[1].slice(0, -1)*1;
                target_button.text("추천 (+"+target_new_like+")")
            };
            
        }, error:function(request,status,error){
            console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);}
    });
}

function vote(grill_id, order, updown) {
    $.ajax({
        type: 'POST',
        url: '/grill/' + grill_id + '/vote_comment/',
        data: {
            grill_comment_order: order,
            is_up: updown,
        },
        dataType: 'json',
        success: function(json){
            
        }, error:function(request, status, error){
            console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);
        }
    });
}


var add_comment = function(grill_id, socket){
        var form_content = $("#new-content").val().replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
        if (!form_content) {
            return false;
        };
        $("#new-content").val('');
        $("#text-counter").text('140');
        $.ajax({
            type: 'POST',
            url: '/grill/'+grill_id+'/add_comment/',
            data: {
                new_content : form_content,
            },
            dataType: 'json',
            success: function(json){
                // emit
                var new_comment_html = json.html;
                $("#comment-content-list").prepend(new_comment_html);
                socket.emit('send_message', new_comment_html);
            },
            error:function(request,status,error){
            console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);}
        });
        return false;
    };

$(document).ready(function(){
            var csrftoken = getCookie('csrftoken');
            var grill_id = document.URL.split("/")[4].split("#")[0]*1;
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $(document).on('click','button.vote-up',function(){
                $(this).attr('disabled',true);
                $(this).parent().children("button.vote-down").attr('disabled', true);
				//vote button이 작동하지 않는 bug
				//vote(grill_id, $($(this)).parentsUntil("#comment-content-list")[4].id.split("-")[1]*1, true);
                var target_new_like = $(this).text().trim().split('+')[1].slice(0, -1)*1 + 1;
                $(this).text("▲추천 (+"+target_new_like+")")
            })

            $(document).on('click','button.vote-down',function(){
                $(this).attr('disabled',true);
                $(this).parent().children("button.vote-up").attr('disabled', true);
                console.log($(this).parentsUntil("#comment-content-list"));
                //vote button이 작동하지 않는 버그
				//vote(grill_id, $($(this)).parentsUntil("#comment-content-list")[4].id.split("-")[1]*1, false);
                var target_new_like = $(this).text().trim().split('-')[1].slice(0, -1)*1 + 1;
                $(this).text("▼반대 (-"+target_new_like+")")
            })

            $("#new-content").on('keyup',function(event){
                var typeable = 140-$($("#new-content")[0]).val().length;
                $("#text-counter").text(typeable);
                if (typeable<0) {
                    $("#btn-add-comment").attr('disabled',true);
                    $("#text-counter").css('color','red');
                } else{
                    $("#btn-add-comment").attr('disabled',false);
                    $("#text-counter").css('color','black');
                }

            })   

            // websocket Initialize
            var socket = io.connect('http://bit.sparcs.org:9779');

            socket.emit('adduser', grill_id);

            // Receive Message
            socket.on('message', function(message){
                $("#comment-content-list").prepend(message);
            });

            // Sending Message
            $("#btn-add-comment").click(function(event){
                event.preventDefault();
                add_comment(grill_id, socket);
            });     

            // 반대 많이 받은 댓글 다시 보여주기
            $(".open-comment").click(function(event){
                event.preventDefault();
                $(this).parent().children(".hate-comment-content").css('display', 'block');
                $(this).parent().children(".hate-content").css('display', 'none');
                $(this).parent().children(".open-comment").css('display', 'none');
            });
        });
