$(document).ready(function(){
    $("span.timeago").timeago();
    var post_order = {{ post.order }};
    var csrf_token = $("input[name=csrfmiddlewaretoken]").val();

    $(".list-post[data-order=" + post_order + "]").addClass('selected');
    $(".list-notice[data-order=" + post_order + "]").addClass('selected');
    $(".numtag").each(function() { 
        order = $(this).data("order");
        $(this).attr("href", "./?cpage=" + Math.ceil(order / 5) + "#comment-" + order);
    });

    var ajax_mark19 = function(obj, url) {
        $.ajax({
            url: url,
            type: "POST",
            data: { csrfmiddlewaretoken: csrf_token },
            success: function(data) {
                alert("19금 신고되었습니다.");
            },
            error: function(data) {
                alert("이미 신고한 항목입니다.");
            }
        });
        obj.attr("disabled", "disabled");
    };

    $(".post-mark19").click(function() {
        ajax_mark19($(this), "./mark19/");
    });

    $(".comment-mark19").click(function() {
        ajax_mark19($(this), "./" + $(this).data("order") + "/mark19/");
    });

    var ajax_delete = function(url) {
        var result = confirm("정말 삭제하시겠습니까?");
        if(result != true) return;

        $.ajax({
            url: url,
            type: "POST",
            data: { csrfmiddlewaretoken: csrf_token },
            success: function(data) {
                location.replace("./");
            }
        });
    };

    $(".post-delete").click(function() {
        ajax_delete("./delete/");
    });
    
    $(".comment-delete").click(function() {
        ajax_delete("./" + $(this).data("order") + "/delete/");
    });

    $(".comment-modify").click(function() {
        var comment_order = $(this).data("order");
        var comment_panel = $(this).parent().parent();
        var is_adult = comment_panel.parent().find("label.adult-mark").length > 0 ? "checked" : "";
        var content = $(".comment-body[data-order=" + comment_order + "]").html().replace(/<br\s*[\/]?>/gi,'');
        console.log(content);
        content = content.replace(/<a class="numtag"[^\>]*>(@\d+)<\/a>/gi, '$1');
        console.log(content);
        var comment_html = "<form action='./" + comment_order + "/modify/{{querystring}}' method='POST'>" +
            "{% csrf_token %}" +
            "<div class='form-group'>" +
                "<textarea class='form-control' rows='2' name='content'>" + content + "</textarea>" + 
                "<div class='checkbox pull-right'><label><input type='checkbox' name='is_adult' " + is_adult + "> 성인 댓글</label></div>" + 
                "<div class='col-md-12'>" +
                    "<button type='submit' class='btn btn-info col-md-1 col-md-offset-11'>완료</button></div></div></form>";
        comment_panel.html(comment_html);
    });
    
    var toggle = function(obj, b, toClass, fromClass) {
        if (!b) {
            t = toClass; toClass = fromClass; fromClass = t;
        }

        obj.removeClass(toClass);
        obj.addClass(fromClass);
    };

    var post_vote = function() {
        var but_up = $(".post-vote-up");
        var result_up = $(".post-vote-number");
        $.ajax({
            url: "./vote/",
            type: "POST",
            data: {csrfmiddlewaretoken: csrf_token},
            success: function(data) {
                result_up.html(data.tup);
            }
        });
    }

    var comment_vote = function(order, up) {
        var result_up = $(".comment-vote-up-result[data-order=" + order + "]");
        var result_down = $(".comment-vote-down-result[data-order=" + order + "]");
        $.ajax({
            url: "./" + order + "/vote/",
            type: "POST",
            data: {csrfmiddlewaretoken: csrf_token, up: up},
            success: function(data) {
                result_up.html(data.tup);
                result_down.html(data.tdown);
            }
        });
    };

    $(".post-vote-up").click(function() {
        console.log("in");
        post_vote($(this));
    });

    $(".vote-up-color").click(function() {
        comment_vote($(this).data('order'), '0');
    });

    $(".vote-down-color").click(function() {
        comment_vote($(this).data('order'), '1');
    });
    
    $(".post-report").click(function(){
        $("#report-form").attr('action', './report/');
        $("#modal-report").modal();
    });

    $(".comment-report").click(function(){
        $("#report-form").attr('action', './' + $(this).data('order') + '/report/');
        $("#modal-report").modal();
    });

    $("#id_content").keyup(function(){
        if ($(this).val() == '')
            $(".report-submit").prop("disabled", true);
        else
            $(".report-submit").prop("disabled", false);
    });

    var frm = $("#report-form");
    frm.submit(function(){
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
            success: function(data){
                alert('신고되었습니다!');
                $("#modal-report").modal('hide');
                $("#id_content").val('');
                $("#id_reason").val('ETC');
                $(".report-submit").prop("disabled", false);
            }
        });
        return false;
    });
});

