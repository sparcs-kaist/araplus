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
        $.ajax({
            type: 'POST',
            url: '/grill/'+grill_id+'/add_comment/',
            data: { new_content : form_content,
                },
            dataType: 'json',
            success: function(json){
                console.log("good");
                var ms = "<li>" + json.author;
                ms += "님이 " + json.commented_at;
                ms += "에 남긴 글 <p>" + json.new_content + "</p></li>";
                $("#result_list").prepend(ms);
                
            },
            error: function(e) {console.log('error:' + e.status);}
        });
    return false;
    };

// using jQuery


