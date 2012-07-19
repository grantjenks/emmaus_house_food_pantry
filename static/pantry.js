function category_options() {
    var options = "";
    _.each(categories, function (category) {
        options += "<option value='"+category+"'>"+category+"</option>";
    });
    return options;
}

function subcategory_options(category) {
    var options = "";
    _.each(subcategories[category], function (subcategory) {
        options += "<option value='"+subcategory+"'>"+subcategory+"</option>";
    });
    return options;
}

function quickedit_dblclick() {
    qe = $(this);
    qe.unbind();
    value = qe.text();
    qe.data("original_value", value);
    if (qe.hasClass("category")) {
        var select_el = "<select name='category_select'>";
        select_el += category_options();
        select_el += "</select>";
        qe.html(select_el);
    } else if (qe.hasClass("subcategory")) {
        parent = qe.parent();
        category = parent.find(".category").text();
        var select_el = "<select name='subcategory_select'>";
        select_el += subcategory_options(category);
        select_el += "</select>";
        qe.html(select_el);
    } else {
        qe.wrapInner("<input type='text' value='"+value+"'></input>");
    }
    qe.keypress(quickedit_enter);
    qe.focusout(quickedit_focusout);
    qe.children().focus();
}

function quickedit_focusout(obj) {
    qe = $(this);
    qe.text(qe.data("original_value"));
    qe.dblclick(quickedit_dblclick);
}

function quickedit_enter(obj) {
    if (obj.which == 13) {
        qe = $(this);
        qe.unbind();
        parts = qe.attr("id").split("-");
        val = qe.children().val();
        $.ajax({
            url: "/inventory/update",
            data: { num: parts[1], field: parts[2], value: val },
            dataType: "json",
            type: "POST",
            async: false,
            cache: false,
            success: function(data) {
                if (parts[2] == "code") {
                    item = data["item"];
                    qe.text(val);
                    parent = qe.parent();
                    parent.find(".name").text(item["name"]);
                    parent.find(".category").text(item["category"]);
                    parent.find(".subcategory").text(item["subcategory"]);
                } else {
                    if (data["update"]) {
                        code = $("#item-"+parts[1]+"-code").text();
                        $(".code").each(function (idx, code_el) {
                            if ($(code_el).text() == code) {
                                id = $(code_el).attr("id");
                                var parent = $("#"+id).parent();
                                parent.find("."+parts[2]).text(val);
                            }
                        });
                        if (parts[2] == "category") {
                            $(".code").each(function (idx, code_el) {
                                if ($(code_el).text() == code) {
                                    id = $(code_el).attr("id");
                                    var parent = $("#"+id).parent();
                                    parent.find(".subcategory").text("");
                                }
                            });
                            alert("Remember to also update the subcategory.");
                        }
                    } else {
                        qe.text(val);
                    }
                }
                qe.dblclick(quickedit_dblclick);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                data = $.parseJSON(jqXHR.responseText);
                alert("Error: " + data["error"]);
                qe.keypress(quickedit_enter);
                qe.focusout(quickedit_focusout);
            }
        });
    }
}

function get_date_formatted() {
    var date = new Date();
    var month = { 0:"Jan", 1:"Feb", 2:"Mar", 3:"Apr", 4:"May", 5:"Jun",
                  6:"Jul", 7:"Aug", 8:"Sep", 9:"Oct", 10:"Nov",
                  11:"Dec" }[date.getMonth()];
    var date_format = month + " " + date.getDate() + ", " + date.getFullYear();
    return date_format;
}

function dist_row(item) {
    var num = item["num"];
    var cols = "<td id='item-"+num+"-code' class='code'>"+item["code"]+"</td>"
        + "<td id='item-"+num+"-name' class='name quickedit'>"+item["name"]+"</td>"
        + "<td id='item-"+num+"-donor' class='quickedit'>"+item["donor"]+"</td>"
        + "<td id='item-"+num+"-release_date' class='quickedit'>"+item["release_date"]+"</td>"
        + "<td id='item-"+num+"-category' class='category quickedit'>"+item["category"]+"</td>"
        + "<td id='item-"+num+"-subcategory' class='subcategory quickedit'>"+item["subcategory"]+"</td>";
    return "<tr>" + cols + "</tr>";
}

function dist_scan_code(obj) {
    if (obj.which == 13) {
        code = $(this).val();
        date = get_date_formatted();
        $.ajax({
            url: "/inventory/release",
            data: { "code": code },
            type: "POST",
            async: false,
            dataType: "json",
            cache: false,
            success: function(item) {
                var row = dist_row(item);
                $(row).find(".quickedit").dblclick(quickedit_dblclick);
                $("tbody").prepend(row);
                $("tbody").children().first().find(".quickedit").dblclick(quickedit_dblclick);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                data = $.parseJSON(jqXHR.responseText);
                alert("Error: " + data["error"]);
            }
        });
        $("#item-code").val("");
    }
}

function rec_new_item_keypress(obj) {
    if (obj.which == 13) {
        rec_new_item();
    }
}

function rec_new_item() {
    var item = {
        code: $("#new-code-in").val(),
        name: $("#new-name-in").val(),
        donor: $("#new-donor-in").val(),
        acquire_date: $("#new-acquire_date-in").val(),
        category: $("#new-category-in").val(),
        subcategory: $("#new-subcategory-in").val()
    };
    $.ajax({
        url: "/inventory/new",
        data: item,
        type: "POST",
        async: false,
        dataType: "json",
        cache: false,
        success: function(item) {
            var id = item["num"];
            var row =  "<tr>"
                + "<td id='item-"+id+"-code' class='code quickedit'>" + item["code"] + "</td>"
                + "<td id='item-"+id+"-name' class='name quickedit'>" + item["name"] + "</td>"
                + "<td id='item-"+id+"-donor' class='quickedit'>" + item["donor"] + "</td>"
                + "<td id='item-"+id+"-acquire_date' class='quickedit'>" + item["acquire_date"] + "</td>"
                + "<td id='item-"+id+"-category' class='category quickedit'>" + item["category"] + "</td>"
                + "<td id='item-"+id+"-subcategory' class='subcategory quickedit'>" + item["subcategory"] + "</td>"
                + "</tr>";
            $("#new-item-row").after(row);
            $("#new-item-row").next().find(".quickedit").dblclick(quickedit_dblclick);
            $("#new-code-in").val("");
            $("#new-name-in").val("");
            $("#new-category-in").val("");
            $("#new-subcategory-in").val("");
            $("#new-code-in").focus();
        },
        error: function(jqXHR, textStatus, errorThrown) {
            data = $.parseJSON(jqXHR.responseText);
            alert("Error: " + data["error"]);
        }
    });
}

function rec_step_1(obj) {
    if (obj.which == 13) {
        $("#new-donor-in").val($("#item-donor").val());
        $("#item-acquire_date").val(get_date_formatted());
        $(".rec-step-2").fadeIn();
        $("#item-acquire_date").focus();
    }
}

function rec_step_2(obj) {
    if (obj.which == 13) {
        $("#new-acquire_date-in").val($("#item-acquire_date").val());
        var receipt_url = $("#create-receipt").attr("href");
        receipt_url += "?donor=" + encodeURIComponent($("#item-donor").val());
        receipt_url += "&acquire_date=" + encodeURIComponent($("#item-acquire_date").val());
        $("#create-receipt").attr("href", receipt_url);
        $(".rec-step-3").fadeIn();
        $("#item-code").focus();
    }
}

function rec_step_3(obj) {
    if (obj.which == 13) {
        code = $("#item-code").val();
        $.ajax({
            url: "/inventory/label",
            data: { "code": code },
            type: "GET",
            async: false,
            dataType: "json",
            cache: false,
            success: function(label) {
                $("#item-name").val(label["name"]);
                $("#item-category").val(label["category"]);
                $("#item-subcategory").val(label["subcategory"]);

                if (label["name"] != ""
                    && label["category"] != ""
                    && label["subcategory"] != "") {
                    rec_step_6_helper();
                } else {
                    var beep = document.getElementById("beep");
                    beep.src = "/static/beep.wav";
                    beep.play();

                    $(".rec-step-4").fadeIn();
                    $("#item-name").focus();

                    if (label["name"] != "") {
                        $(".rec-step-5").fadeIn();
                        $("#item-category").focus();
                    }

                    if (label["category"] != "") {
                        $(".rec-step-6").fadeIn();
                        $("#item-subcategory").focus();
                    }
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                data = $.parseJSON(jqXHR.responseText);
                alert("Error: " + data["error"]);
            }
        });
    }
}

function rec_step_4(obj) {
    if (obj.which == 13) {
        $("#item-category").html(category_options());
        $(".rec-step-5").fadeIn();
        $("#item-category").focus();
    }
}

function rec_step_5(obj) {
    if (obj.which == 13) {
        var category = $("#item-category").val();
        $("#item-subcategory").html(subcategory_options(category));
        $(".rec-step-6").fadeIn();
        $("#item-subcategory").focus();
    }
}

function rec_step_6_helper() {
    $("#new-donor-in").val($("#item-donor").val());
    $("#new-acquire_date-in").val($("#item-acquire_date").val());
    $("#new-code-in").val($("#item-code").val());
    $("#new-name-in").val($("#item-name").val());
    $("#new-category-in").val($("#item-category").val());
    $("#new-subcategory-in").val($("#item-subcategory").val());

    rec_new_item();

    // TODO: Error handling?

    $(".rec-step-6").fadeOut();
    $("#item-subcategory").val("");

    $(".rec-step-5").fadeOut();
    $("#item-category").val("");

    $(".rec-step-4").fadeOut();
    $("#item-name").val("");

    $("#item-code").val("");
    $("#item-code").focus();
}

function rec_step_6(obj) {
    if (obj.which == 13) {
        rec_step_6_helper();
    }
}

function rcpt_step_1(obj) {
    if (obj.which == 13) {
        $("#item-acquire_date").val(get_date_formatted());
        $(".rcpt-step-2").fadeIn();
        $("#item-acquire_date").focus();
    }
}

function rcpt_step_2(obj) {
    if (obj.which == 13) {
        var receipt_url = $("#create-receipt").attr("href");
        receipt_url += "?donor=" + encodeURIComponent($("#item-donor").val());
        receipt_url += "&acquire_date=" + encodeURIComponent($("#item-acquire_date").val());
        $("#create-receipt").attr("href", receipt_url);
        $(".rcpt-step-3").fadeIn();
        $("#create-receipt").focus();
    }
}

function trash_dblclick() {
    var col = $(this);
    var row = col.parent();
    var ans = confirm("Are you sure you want to delete this item?");
    var parts = col.attr("id").split("-");
    if (ans) {
        $.ajax({
            url: "/inventory/delete",
            data: { num: parts[1] },
            dataType: "json",
            type: "POST",
            async: false,
            cache: false,
            success: function(data) {
                row.remove();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                var data = $.parseJSON(jqXHR.responseText);
                alert("Error: " + data["error"]);
            }
        });
    } else {

    }
}
