var query_filter = "grade=1&class_=&school=BB&school=BX&prop=Y&prop=W";
var cur_page = 1;
function query_student_list(page = 1, update_filter = false) {
    console.log("querying");
    var btn_query = $("#id-btn-query");
    var query_form = $("#id-query-form");

    if (update_filter) {
        query_filter = query_form.serialize();
    }
    $.ajax({
        url: "/crew/student/",
        type: "POST",
        data: query_filter + "&page=" + page,
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

var old_content = "";
function view_student(student_id) {
    old_content = $("#id-main-content").html();
    $.ajax({
        url: "/crew/student/" + student_id,
        type: 'GET',
        success: function (data) {
            if (data['ok']) {
                $("#id-main-content").html(data['content_html'])
            } else {
                show_message("danger", data['message']);
            }
        },
        error: function () {
            show_message("danger", "服务器错误");
        }
    });
}

function update_student() {
    var form = $('#id-student-form');
    var action = form.attr('action');
    console.log("update " + action);
    $('#id-btn-save').addClass('disabled');
    $('#id-btn-save').val('保存中');
    $.ajax({
        url: action,
        type: 'POST',
        data: form.serialize(),
        success: function (data) {
            if (data['ok']) {
                show_message('success', "保存成功");
                console.log("update done");
            } else {
                console.log("update fail");
            }
            $("#id-main-content").html(data['content_html'])
        },
        error: function () {
            alert("错误");
        }
    });
}

function delete_student(student_id) {
    console.log("delete " + student_id);
    $.ajax({
        url: '/crew/student/' + student_id,
        type: 'DELETE',
        success: function (data) {
            if (data['ok']) {
                show_message('success', "删除成功");
                query_student_list(cur_page, false);
            } else {
                show_message('danger', data['message']);
            }
        },
        error: function () {
            show_message('danger', "出错");
        }
    })
}

var timer = undefined
function show_message(type, message, duration = 1) {
    $('#id-message').html('<div class="alert alert-' + type + '" role="alert">' + message + '</div>');
    $('#id-message').show();
    if(timer){
        clearTimeout(timer);
    }
    timer = setTimeout(function(){
        $('#id-message').fadeOut();
    }, duration*1000);
}

$(function () {
    var btn_query = $("#id-btn-query");
    btn_query.click(query_student_list.bind(1, true));
    $('body').on('click', '#id-btn-save', update_student);
    $('body').on('click', '#id-btn-back', function () {
        $('#id-main-content').html(old_content);
    });

    query_student_list(1, false);
});

