var query_filter = "grade=1&class_=&school=BB&school=BX&prop=Y&prop=W";
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
            } else {
                console.log("fail");
            }
            query_form.html(data['form_html']);
        },
        error: function () {
            btn_query.attr("disabled", false);
            console.log("err");
        }
    });
}

function view_student(student_id) {
    $.ajax({
        url: "/crew/student/" + student_id,
        type: 'GET',
        success: function (data) {
            if(data['ok']){
                $("#id-main-content").html(data['content_html'])
            } else {
                alert(data['message'])
            }
        },
        error: function () {
            alert("服务器错误")
        }
    });
}

function edit_student() {
    console.log("edit " + student_id);
}

function delete_student(student_id) {
    console.log("delete " + student_id);
}

$(function () {
    var btn_query = $("#id-btn-query");
    btn_query.click(query_student_list.bind(1, true));
    query_student_list(1, false);
});

