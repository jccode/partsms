
jQuery(function($) {

    // init
    $("#id_employee_0").on("djselectableselect", auto_complete_employee_num_and_department);



    // functions

    function auto_complete_employee_num_and_department() {
        var employee_name = $("#id_employee_0").val(),
            $employee_num = $("#id_employee_num"),
            $department = $("#id_department");
        
        $.getJSON("/api/employee/?user__username="+employee_name).done(function(data) {
            if(data.count > 0) {
                var ret = data.results[0];
                $employee_num.val(ret.num ? ret.num : "");
                $department.val(ret.department ? ret.department.name : "");
            }
        });
    }
});


