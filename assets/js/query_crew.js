function query_student_list(page=1) {
    console.log("querying");
    var btn_query = $("#id-btn-query");
    var query_form = $("#id-query-form");
    $.ajax({
        url: "/crew/student/?page="+page,
        type: "POST",
        data: query_form.serialize(),
        success: function (data) {
            btn_query.attr("disabled", false);
            if (data['ok']) {
                console.log("ok");
                $("#id-main-content").html(data['data_html'])
            } else {
                console.log("fail");
            }
            query_form.html(data['form_html'])
        },
        error: function () {
            btn_query.attr("disabled", false);
            console.log("err");
        }
    });
}

$(function () {
    var btn_query = $("#id-btn-query");
    btn_query.click(query_student_list);
});

