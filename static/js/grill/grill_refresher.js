var refresh_timer;
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
    if ($($("#result_list>li")[0]).attr("id") != null)
    {
        current_index = $($("#result_list>li")[0]).attr("id").split("_")[1];
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
            //Update Comments
            for (var i = json.comments.length - 1; i >= 0; i--) {
                var target = json.comments[i];
                var options = {
                    year: "numeric", month: "short",
                    day: "numeric", hour: "2-digit", minute: "2-digit"
                };
                var temp_date = new Date(target.created_time);
				/*
                var ms = '<li id="comment_'+target.order+'">' + target.order +"번째. "+target.author;
                ms += "님이 " + temp_date.toLocaleTimeString("ko-KR",options)
                ms += "에 남긴 글 <p>" + target.content + ' <button class="vote_up"> 추천 (+0)</button></p></li>';*/

				var ms = '<li id="comment_'+target.order+'" class="a-comment-of-list">';
				ms += '<div class="a-comment-area">';
				ms += '	<span>'+target.order+'</span>';
				ms += '<div class="a-comment-content">'+target.content+'</div>';
				ms += '<div class="a-comment-info">';
				ms += '<div class="a-comment-author-container">';
				ms += '<span>'+target.author+'</span>';
				ms += '<span class="a-comment-date">'+temp_date.toLocaleTimeString("ko-KR", options)+'</span>';
				ms += '</div>';
				ms += '<div class="a-comment-vote-container">';
				ms += '<button class="vote_up a-comment-vote"> 추천 (+0) </button>';
				ms += '</div></div></div></li>';

                $("#result_list").prepend(ms);   
            };

            //Update Votes
            last_update = json.last_update
            if (!json.new_votes) {
                return false;
            };
            for (var i = json.new_votes.length - 1; i >= 0; i--) {
                var target = json.new_votes[i]
                var target_order = target.grill_comment
                var target_new_like = target.new_count
                var target_button = $($("#comment_"+target_order).find("button")[0])
                target_new_like += target_button.text().trim().split('+')[1].slice(0, -1)*1;
                target_button.text("추천 (+"+target_new_like+")")
            };
            
        }, error:function(request,status,error){
            console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);}
    });
}

function vote(grill_id, order, updown) {
    console.log("grill_id : " + grill_id + "/"+typeof(grill_id))
    console.log("order : " + order + "/"+typeof(order) )
    $.ajax({
        type: 'POST',
        url: '/grill/' + grill_id + '/vote_comment/',
        data: {
            grill_comment_order: order,
            is_up: updown,
        },
        dataType: 'json',
        success: function(json){
            clearInterval(refresh_timer);
            refresh_comment(grill_id);
            refresh_timer = setInterval(function(){
                refresh_comment(grill_id);},5000);
        }, error:function(request,status,error){
            console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);}
    });
}


var add_comment = function(grill_id, socket){
        var form_content = $("#new_content").val().replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
        if (!form_content) {
            return false;
        };
        $("#new_content").val('');
        $.ajax({
            type: 'POST',
            url: '/grill/'+grill_id+'/add_comment/',
            data: { new_content : form_content,
                },
            dataType: 'json',
            success: function(json){
                // emit
                var new_comment_html = json.html;
                $("#result_list").prepend(new_comment_html);
                socket.emit('send_message',new_comment_html);
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

            // refresh_timer = setInterval(function(){refresh_comment(grill_id);},5000);

            //$(document).on('click','button.vote_up',function(){
            //    console.log(grill_id);
            //    console.log(true);
            //    $(this).attr('disabled',true);
            //    vote(grill_id, $($(this)).parentsUntil("#result_list")[3].id.split("_")[1]*1, true);
//
  //          })
    //        $(document).on('click','button.vote_down',function(){
      //          console.log(grill_id);
        //        console.log(false);
          //      $(this).attr('disabled',false);
            //     vote(grill_id, $($(this)).parentsUntil("#result_list")[3].id.split("_")[1]*1, false);
           // })

            $("#new_content").on('keyup',function(event){
                $("#text_counter").text($($("#new_content")[0]).val().length);
            })   

        // websocket part
            var socket = io.connect('http://localhost:9779');


            socket.on('connect', function(){
                console.log("connection made with " + grill_id);
            })

            socket.emit('adduser',grill_id);
            
            // Receive Message
            socket.on('message', function(message){
                console.log("message : " + message);
                $("#result_list").prepend(message);
            });

            // Sending Message
            $("#add_comment_button").click(function(event){
                console.log("HI")
                event.preventDefault();
                add_comment(grill_id, socket);
            });     

            $(".open_comment").click(function(event){
                console.log("open!")
                console.log($(this).parent().children("#hate_comment_content"))
                $(this).parent().children("#hate_comment_content").css('display', 'block');
                $(this).parent().children("#hate_content").css('display', 'none');
                $(this).parent().children(".open_comment").css('display', 'none');
                event.preventDefault();
            });
        });
