var query_filter = "";
var cur_page = 1;
function query_record(page = 1, update_filter = false, edit = false) {
    console.log("querying");
    var btn_query = $("#id-btn-query");
    var query_form = $("#id-query-form");
    $('#id-main-content').html("");

    if (update_filter) {
        query_filter = query_form.serialize();
    }
    var params = {
        'page': page
    };
    if (edit) {
        params['edit'] = 1
    }
    $.ajax({
        url: "/crew/record/input",
        type: "GET",
        data: query_filter + '&' + $.param(params),
        success: function (data) {
            btn_query.attr("disabled", false);
            if (data['ok']) {
                $("#id-main-content").html(data['content_html'])
                cur_page = page;
            } else {
            }
            query_form.html(data['form_html']);
        },
        error: function () {
            btn_query.attr("disabled", false);
            console.log("err");
            show_message("danger", "出错");
        }
    });
}

function save_record() {
    data = [];
    $('#id-table-record').find("input").each(function (i, e) {
        data[i] = {'student_id': $(e).data('student-id'), 'score': $(e).val()};
    });
    console.log(data);
    $('#id-btn-save').addClass('disabled').text("保存中");
    $.ajax({
        url: "/crew/record/input",
        type: "POST",
        data: $.param({'data': JSON.stringify(data)}) + '&' + query_filter,
        success: function (data) {
            $('#id-btn-save').addClass('disabled').text("保存");
            if (data['ok']) {
                show_message("success", "保存成功");
            } else {
                show_message("danger", data["msg"]);
            }
        },
        error: function () {
            $('#id-btn-save').addClass('disabled').text("保存");
            show_message("danger", "出错");
        }
    })
}

var timer = undefined;
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
    $("#id-btn-edit").click(function () {
        query_record(1, true);
    });
    $("body").on("click", "#id-btn-save", save_record);
});

