
jQuery(function($) {
    
    $("#id_employee_0").on("djselectableselect", function(e) {
        // console.log( '领用人改了啊...' );
    });



    // functions

    function auto_complete_employee_num_and_department() {
        var employee_name = $("#id_employee_0").val(),
            $employee_num = $("#id_employee_num"),
            $department = $("#id_department");
        // TODO : AJAX auto fill these two fields
    }
});


