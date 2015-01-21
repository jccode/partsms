
jQuery(function($) {

    // init
    show_repair_obsolete_btn_or_not();
    show_stock_in_num_field_or_not();

    // bind event
    $("#id_repaireable").on("change", show_repair_obsolete_btn_or_not);
    $("#id_status_after_repaired").on("change", show_stock_in_num_field_or_not);
});

function show_repair_obsolete_btn_or_not() {
    var repairable = $("#id_repaireable").val(),
        repair_btn = $(":input[name='_fsmtransition-repair']"),
        obsolete_btn = $(":input[name='_fsmtransition-obsolete']");
    if(repairable == 1) {
        repair_btn.hide();
        obsolete_btn.hide();
    }
    else if(repairable == 2) {
        repair_btn.show();
        obsolete_btn.hide();
    }
    else {
        repair_btn.hide();
        obsolete_btn.show();
    }
}

function show_stock_in_num_field_or_not() {
    var status_after_repaired = $("#id_status_after_repaired").val(),
        row_stock_in = $("div.form-row.field-store_in_num");
    if(status_after_repaired && status_after_repaired == 'Repaied') {
        row_stock_in.show();
    }
    else {
        row_stock_in.hide();
        $("#id_store_in_date").val("");
        $("#id_store_in_num").val("");
    }
}

