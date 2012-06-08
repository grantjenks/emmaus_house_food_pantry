function quickedit_dblclick() {
    qe = $(this);
    qe.unbind();
    value = qe.text();
    qe.data("original_value", value);
    qe.wrapInner("<input type='text' value='"+value+"'></input>");
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
                                $("#"+id).parent().find("."+parts[2]).text(val);
                            }
                        });
                    } else {
                        qe.text(val);
                    }
                }
                qe.dblclick(quickedit_dblclick);
            },
            error: function() {
                alert("Error.");
                qe.keypress(quickedit_enter);
            }
        });
    }
}

$(document).ready(function() {
    $(".quickedit").dblclick(quickedit_dblclick);
});
