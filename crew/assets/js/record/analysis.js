var query_filter = "";
var cur_page = 1;
function query_record(page, update_filter, sort_by, ascending) {
    console.log("querying");
    console.log(ascending)
    var btn_query = $("#id-btn-query");
    var query_form = $("#id-query-form");
    $('#id-main-content').html("");

    if (update_filter) {
        query_filter = query_form.serialize();
    }
    var params = {
        'page': page,
        'sort_by': sort_by,
        'ascending': ascending? 1 : 0
    };
    $.ajax({
        url: "/crew/record/api_analysis",
        type: "GET",
        data: query_filter + '&' + $.param(params),
        success: function (data) {
            btn_query.attr("disabled", false);
            if (data['ok']) {
                $("#id-main-content").html(data['content_html'])
                cur_page = page;
            } else {
                show_message("danger", data['msg'])
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

var timer = undefined;
function show_message(type, message, duration) {
    if(duration === undefined){
        duration = 5;
    }
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
    $("#id-btn-stat").click(function () {
        query_record(1, true, "总分", false);
    });

    var current_sort_key = '总分';
    var current_ascending = false;
    $("body").on("click", ".rank-table .subject, .rank-table .score, .rank-table .rank, .rank-table .student-id", function () {
        var new_sort_key = $(this).data('key');
        if(new_sort_key == current_sort_key){
            current_ascending = !current_ascending;
        } else {
            current_sort_key = new_sort_key;
            if(new_sort_key=='student_id'){
                current_ascending = true;
            } else {
                current_ascending = false;
            }
        }
        console.log("sort " + new_sort_key + ' ' + current_ascending);
        query_record(1, false, current_sort_key, current_ascending);
    });
});
