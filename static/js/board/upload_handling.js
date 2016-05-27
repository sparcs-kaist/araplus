// update index of input element
function updateElementIndex(el, prefix, index){
    var id_regex = new RegExp('(' + prefix + '-\\d+-)');
    var replacement = prefix + '-' + index + '-';
    if($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if(el.id) el.id = el.id.replace(id_regex, replacement);
    if(el.name) el.name = el.name.replace(id_regex,replacement);
}
$(document).ready(function(){
    // dynamically add and remove file upload field
    $("input[type=file]").change(function(){
        var formCount = parseInt($("#id_form-TOTAL_FORMS").val());
        // 만약 빈 파일로 바뀌었을 경우 항목 삭제
        if(!$(this).val()){
            // 만약 입력란이 한 개 일 때는 그냥 항목만 삭제
            if(formCount == 1) return;
            // 그 외의 경우에는 입력 form을 삭제한다
            else{
                parent_div = $(this).parent().parent().parent();
                parent_div.slideUp(300, function(){
                    $(this).remove();
                });
                var forms = $(".attachment");
                // Update total numbers of file form
                $("#id_form-TOTAL_FORMS").val(forms.length - 1);
                var i = $.inArray(parent_div.get(0), forms) + 1;
                for(formCount = forms.length; i < formCount; i++){
                    hidden_input = $(forms.get(i)).children().get(0);
                    label_for_input = $(forms.get(i)).children().children().get(0);
                    file_input = $(forms.get(i)).children().children().children().get(0);
                    updateElementIndex(hidden_input, 'form', i-1);
                    updateElementIndex(label_for_input, 'form', i-1);
                    updateElementIndex(file_input, 'form', i-1);
                }
            }
        }
        // 빈 파일이 아닌 것으로 변경 되었을 때
        else{
            forms = $(".attachment");
            parent_div = $(this).parent().parent().parent().get(0);
            index_of = $.inArray(parent_div, forms);
            // 총 업로드한 파일의 갯수가 10 개 이하이고 마지막 element일 때
            // element 추가.
            if(formCount < 10 && index_of +1 == formCount){
                //add new input element
                var row = $(".attachment:last").clone(true).get(0);
                hidden_input = $(row).children().get(0);
                label_for_input = $(row).children().children().get(0);
                file_input = $(row).children().children().children().get(0);
                updateElementIndex(hidden_input, 'form', formCount);
                updateElementIndex(label_for_input, 'form', formCount);
                updateElementIndex(file_input, 'form', formCount);
                $(row).hide().insertAfter(".attachment:last").slideDown(300);
                // update totla number of forms
                $("#id_form-TOTAL_FORMS").val(formCount + 1);
            }
            else return;
        }
    });
});
