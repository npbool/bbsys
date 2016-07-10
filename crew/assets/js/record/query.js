var query_filter = "";
var cur_page = 1;
function query_record(page = 1, update_filter = false, edit=false) {
    console.log("querying");
    var btn_query = $("#id-btn-query");
    var query_form = $("#id-query-form");

    if (update_filter) {
        query_filter = query_form.serialize();
    }
    var params = {
        'page': page
    };
    if(edit){
        params['edit'] = 1
    }
    $.ajax({
        url: "/crew/record/",
        type: "GET",
        data: query_filter + '&' + $.param(params),
        success: function (data) {
            btn_query.attr("disabled", false);
            if (data['ok']) {
                console.log("ok");
                $("#id-main-content").html(data['content_html'])
                cur_page = page;
            } else {
                console.log("fail");
            }
            query_form.html(data['form_html']);
        },
        error: function () {
            btn_query.attr("disabled", false);
            console.log("err");
            show_message("danger", "服务器错误");
        }
    });
}

// Util
var old_content = "";
function save_content(){
    old_content = $('#id-main-content').html();
}
function restore_content(){
    $('#id-main-content').html(old_content);
}

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
    $("#id-btn-query").click(function () {
        query_record(1, true);
    });
    $("#id-btn-edit").click(function () {
        query_record(1, true, true);
    })
});

