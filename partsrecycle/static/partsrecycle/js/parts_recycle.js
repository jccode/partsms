
jQuery(function($) {

    // init
    show_repair_obsolete_btn_or_not();

    // bind event
    $("#id_repaireable").on("change", show_repair_obsolete_btn_or_not);
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
