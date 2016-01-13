$(document).ready(function(){
    /* 선택한 게시물 style 변경 */
    selected_post = location.href.split('/')[5];
    $("#post-row-"+selected_post).addClass('selected');
    /* <!-- --------------------- --> */
    $(".comment").click(function(){
        var board_comment_order = $(this).attr("id").split('-')[1];
        var board_comment_id = $(this).attr("id").split('-')[2];
        var content = $("#comment"+board_comment_order).text().replace(/<br\s*[\/]?>/gi,'\n');
        var mod_comment = "<div class='comment-modify-wrapper'>"+
        "<form action='./comment_mod/' method='POST' class='comment_modify_form' enctype='multipart/form-data'>"+
            "<input type='hidden' name='csrfmiddlewaretoken' value=" + 
                $("input[name=csrfmiddlewaretoken]").val() + ">" +
            "<input type='hidden' name='board_comment_id' value=" + board_comment_id + ">"+ 
            "<textarea class='comment-textarea' rows='4' name='content'>"+
            content+
            "</textarea>"+
            "<button type='Submit' class='comment-modify-button'>"+
            "완료"+
            "</button></form></div>";
        $(mod_comment).replaceAll("#comment_content"+board_comment_order);
    });
    $(".vote").click(function() {
        var vote_id = $(this).attr("id").split('_'); 
        console.log(vote_id[0] + vote_id[1]);
        $.ajax(
        {
            url : "vote/",
            type : "POST",
            data : { vote_type : vote_id[0], vote_id : vote_id[1], csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()},
            dataType : 'json',
            success : function(data){
                console.log(data.response);
                if(data.response == 'success'){
                    $("#vote_up_"+vote_id[1]).html(data.vote.up);
                    $("#vote_down_"+vote_id[1]).html(data.vote.down);
                    $("#post-vote-up-"+vote_id[1]).html(data.vote.up);
                    $("#post-vote-down-"+vote_id[1]).html(data.vote.down);
                    alert(data.message);
                }
                else{
                    alert('Failed');
                }
            }
        });
    });
    $(".delete").click(function() {
        var yes=confirm("Do yo REALLY want to delete?");
        if(yes == true){
            var delete_uid=$(this).attr("id").slice(7);
            $.ajax({
                url: "delete/",
                type : "POST",
                data:{id: delete_uid,
                    csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()},
                success: function(data){
                    location.reload();
                }
            });
            return true;
        }
        else{
            return false;
        }
    });
    function toggle(obj,toclass,fromclass) {
        if(obj.hasClass(toclass)){
            obj.removeClass(toclass);
            obj.addClass(fromclass);
        }
    }
    $(".report_submit").click(function() {
        var report_reason = $("#report_reason").val()
        var report_content = $("#report_content").val()
        $.ajax({
            url : "report/",
            type : "POST",
            data : { id : report_uid, report_reason : report_reason, report_content : report_content,csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()},
            success : function(data){
                alert(data);
            }
        });
        doOverlayClose();
    });
    $(".reason").click(function(){
        var bid = $(this).attr("id");
        var bname = $(this).text() + " <span class='caret'></span>";
        $("#report_reason").attr("value", bid);
        $("#report_reason_dropdown").html(bname);
    });
    $(".report").click(function(){
        $("#modal-report").modal();
        var content_id = $(this).attr('id').split('_')[1];
        $("#content_id").attr("value", content_id);
    });
    var frm = $("#form_report");
    frm.submit(function(){
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
            success: function(data){
                if (data.message != 'Invalid form'){
                    alert(data.message)
                    $("#id_content").val('');
                    $("#id_reason").val('기타');
                    $("#modal-report").modal('hide');
                }
                else{
                    alert(data.message)
                }
            }
        });
        return false
    });
    
	var hoverHTMLDemoBasic = '<p></p><p class="tempSpace"></p>';
    
	$(".comment_preview").hovercard({
        detailsHTML : hoverHTMLDemoBasic,
        width: 400,
        onHoverIn: function() {
            console.log($(".comment_preview_content")[0]);
            if(typeof($(".comment_preview_content")[0]) != "undefined") $(".comment_preview_content").remove();

            var order = $(this).children('a').attr('title').split('_')[1];
            var content = document.getElementById('comment'+order).textContent;
            $(".tempSpace").append('<span class="comment_preview_content">' + content + '</span>');
        },
        onHoverOut: function() {
            /*$(".comment_preview_content").remove();*/
        }
    });


    // for trace post
    $(".trace, .alarm").click(function(){
        var post_id = $(this).attr("id").split("-")[1];
        $.ajax(
        {
            url: "trace/",
            type: "POST",
            data: {
                type: $(this).attr("id").split("-")[0],
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function(data){
                trace_obj = $(".trace");
                alarm_obj = $(".alarm");
                if(data.trace){
                    trace_obj.removeClass('glyphicon-star-empty');
                    trace_obj.addClass('tracing');
                    trace_obj.addClass('glyphicon-star');
                }
                else{
                    trace_obj.removeClass('tracing');
                    trace_obj.removeClass('glyphicon-star');
                    trace_obj.addClass('glyphicon-star-empty');
                }
                if(data.alarm){
                    alarm_obj.removeAttr('style');
                    alarm_obj.addClass('activated');
                }
                else{
                    alarm_obj.removeClass('activated');
                    alarm_obj.css('color', "white");
                }
            }
        });
    });
    $(".hiddenContent").click(function(){
        $(this).html($(this).attr("value"));
    });

    $('.comment-write-button').click(function(){
        $(this).parent().parent().submit();
        $(this).attr('disabled', 'disabled');
    });
});
