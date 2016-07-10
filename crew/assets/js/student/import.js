var timer = undefined
function show_message(type, message, duration = 1) {
    $('#id-message').html('<div class="alert alert-' + type + '" role="alert">' + message + '</div>');
    $('#id-message').show();
    if (timer) {
        clearTimeout(timer);
    }
    timer = setTimeout(function () {
        $('#id-message').fadeOut();
    }, duration * 1000);
}

$(function () {
    $('#id-file-upload').fileupload({
        dataType: 'json',
        url: '/crew/import/',
        options: {
            acceptFileTypes: /(\.|\/)(xls)$/i,
        },
        add: function (e, data) {
            console.log(data);
            if(!data.files[0].name.endsWith(".xls") || data.files[0].name.endsWith(".XLS")){
                alert("请选择xls文件(不支持xlsx)")
                return;
            }
            $("#id-file-name").val(data.files[0].name);
            $("#id-file-submit").removeClass("disabled");
            $("#id-file-submit").unbind("click").click(function () {
                $("#id-file-submit").text("处理中...").addClass("disabled");
                data.submit();
            });
        },
        done: function (e, data) {
            $("#id-file-name").val('');
            if(data.result['ok']){
                show_message("success","导入成功");
            } else {
                show_message("danger","导入失败");
            }
            $("#id-file-submit").text("导入").addClass("disabled");
            console.log(data.result);
            console.log(data.textStatus);
            console.log(data.jqXHR);
        }
    })
});