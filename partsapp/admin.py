from django.contrib import admin
from django import forms

from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.admin.sites import site
from django.contrib.auth import models as auth

from partsapp.models import PartsRequest, RequestDetail, PartsRecycle
from dept.models import Employee
from django.utils.translation import ugettext as _



class RequestDetailInlineForm(forms.ModelForm):
    
    class Meta:
        widgets = {
            'remark': forms.TextInput(attrs={'size': 20}),
        }
    

class RequestDetailInline(admin.TabularInline):
    model = RequestDetail
    form = RequestDetailInlineForm
    extra = 1

    
class RequestAdminForm(forms.ModelForm):
    # approver = forms.ModelMultipleChoiceField(label=_('Approver'),
    #                                           widget=forms.SelectMultiple,
    #                                           queryset=Employee.objects.all())

    approver = forms.ModelMultipleChoiceField(queryset=Employee.objects.all(), 
                                              widget=FilteredSelectMultiple(_("Approver"),
                                                                            is_stacked=False),
                                              label=_('Approver'))

    class Meta:
        model = PartsRequest
        

class RequestAdmin(admin.ModelAdmin):
    form = RequestAdminForm
    inlines = [RequestDetailInline]
    list_display = ('request_no', 'apply_type', 'material_type', 'request_date', 'apply_reason',
                    'department', 'employee_num',
                    'employee', 'cost_center', 'approver_name', )

    def department(self, obj):
        return obj.employee.department
    department.short_description = _('department')

    def employee_num(self, obj):
        return obj.employee.num
    employee_num.short_description = _('employee number')

    def approver_name(self, obj):
        approver_ids = obj.approver
        approvers = map(lambda uid: auth.User.objects.get(id=uid).username, approver_ids.split(','))
        return "[%s]" % (", ".join(approvers))
    approver_name.short_description = _('Approver')

    # def get_form(self, request, obj=None, **kwargs):
    #     if not obj:
    #         return RequestAdminForm
    #     return super(RequestAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        approver = form.cleaned_data.get('approver')
        approver_ids = map(lambda user: str(user.id), approver)
        obj.approver = ",".join(approver_ids)
        obj.save()
        
    class Media:
        css = {
            "all": ("partsapp/css/parts_request.css", )
        }
        js = ("partsapp/js/parts_request.js", )
        

class PartsRecycleForm(forms.ModelForm):
    pass

        
class PartsRecycleAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Parts'), {
            'fields': ('request_no', 'parts', 'pn', 'sn', 'tool', 'stn')
        }),
        (_('Recycle'), {
            'fields': ('employee', 'supervisor', 'manager', 'shift', 'return_date',
                       'status_before_recycle', 'description')
        }),
        (_('Approve'), {
            'fields': ('approver', 'approve_date', 'confirm_result', 'remark_approved')
        }),
        (_('Engineer Approve'), {
            'fields': ('engineer_approver', 'engineer_approve_date', 'repaireable',
                       'engineer_ack_status', 'remark_engineer')
        }),
        (_('Repair'), {
            'fields': ('repairer', 'repair_date', 'remark_repairer', 'status_after_repaired',
                       'store_in_date', 'store_in_num')
        })
    )
    

        
# Register your models here.
admin.site.register(PartsRequest, RequestAdmin)
# admin.site.register(RequestDetail)
admin.site.register(PartsRecycle, PartsRecycleAdmin)
