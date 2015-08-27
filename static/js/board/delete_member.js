$(document).ready(function() {
    $(".delete_member").click(function() {
        var member_name = $(this).attr("value");
        $.ajax(
        {
            url : "delete_member/",
            type : "POST",
            data : { member_name: member_name, csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()},
            success : function(data){
                location.reload();
            }
        });
    });
});
