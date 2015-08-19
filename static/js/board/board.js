$(document).ready(function(){
    /* 선택한 게시물 style 변경 */
    selected_post = location.href.split('/')[5];
    $("#post-row-"+selected_post).addClass('selected');
    /* <!-- --------------------- --> */
    $(".comment").click(function(){
        var board_comment_id=$(this).attr("id").slice(3);
        var content = $("#comment"+board_comment_id).html().replace(/<br\s*[\/]?>/gi,'\n');
        var mod_comment = "<form action='./comment_mod/{{querystring}}' method='POST'>"+
            "{% csrf_token %}"+
            "<input type='hidden' name='board_comment_id' value=" + board_comment_id + ">"+ 
            "<input type='hidden' name='board_post_id' value={{post.id}}>"+
            "<div class='form-group'>"+
            "<textarea class='form-control' rows='2' name='content'>"+
            content+
            "</textarea>"+
            "<div class='col-md-12'>"+
            "<button type='submit' class='btn btn-info col-md-1 col-md-offset-11'>"+
            "완료"+
            "</button></div></div></form>";
        $(mod_comment).replaceAll("#comment_content"+board_comment_id);
    });
    $(".vote").click(function() {
        var vote_id = $(this).attr("id").split('_'); 
        var vote_up = $("#up_"+vote_id[1]);
        var vote_down = $("#down_"+vote_id[1]);
        console.log(vote_id[0] + vote_id[1]);
        $.ajax(
        {
            url : "vote/",
            type : "POST",
            data : { vote_type : vote_id[0], vote_id : vote_id[1], csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()},
            dataType : 'json',
            success : function(data){
                if(data.response == 'success'){
                    $("#vote_"+vote_id[1]).html("추천 +"+data.vote.up+"/-"+data.vote.down);
                    if(data.cancel == 'no' || data.cancel == 'yes')
                    {
                        toggle(vote_up, 'btn-warning', 'btn-success');
                        toggle(vote_down, 'btn-warning', 'btn-danger');
                        if(vote_id[0] == 'up' && data.cancel == 'no') toggle(vote_up, 'btn-success', 'btn-warning');
                        if(vote_id[0] == 'down' && data.cancel == 'no') toggle(vote_down, 'btn-danger', 'btn-warning');
                    }
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
                data:{id: delete_uid, csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()},
                success: function(data){
                    console.log(data);
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
    <!-- for trace post -->
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
});
