from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from dept.models import Employee, Department
from django.utils.translation import ugettext as _

class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'employee'

    
class UserAdmin(UserAdmin):
    inlines = (EmployeeInline, )
    list_display = UserAdmin.list_display + ('employee_number', 'department', )

    def employee_number(self, obj):
        return obj.employee.num
    employee_number.short_description = _('employee number')

    def department(self, obj):
        return obj.employee.department
    department.short_description = _('department')



# Register your models here.
admin.site.register(Department)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
