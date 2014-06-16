from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.admin.sites import site
from django.contrib.auth import models as auth
from django.utils.translation import ugettext as _
from fsm_admin.mixins import FSMTransitionMixin
from partsapp.models import PartsRequest, RequestDetail, PartsRecycle, Status
from dept.models import Employee



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


class PartsRecycleAdmin(FSMTransitionMixin, admin.ModelAdmin):
    _fields = [
        {
            'group': 'Parts', 
            'status': Status.DRAFT, 
            'fields': ('request_no', 'parts', 'pn', 'sn', 'tool', 'stn'),
        }, 
        {
            'group': 'Recycle', 
            'status': Status.DRAFT, 
            'fields': ('employee', 'supervisor', 'manager', 'shift', 'return_date',
                       'status_before_recycle', 'description'), 
        }, 
        {
            'group': 'Approve', 
            'status': Status.SUPERVISOR_APPROVE, 
            'fields': ('approver', 'approve_date', 'confirm_result', 'remark_approved'), 
        }, 
        {
            'group': 'Engineer Approve', 
            'status': Status.ENGINEER_APPROVE, 
            'fields': ('engineer_approver', 'engineer_approve_date', 'repaireable',
                       'engineer_ack_status', 'remark_engineer'), 
        }, 
        {
            'group': 'Repair', 
            'status': Status.REPAIR, 
            'fields': ('repairer', 'repair_date', 'remark_repairer', 'status_after_repaired',
                       'store_in_date', 'store_in_num')
        }
    ]

    list_display = ('request_no', 'parts', 'pn', 'sn', 'tool', 'stn', 'employee', 'shift',
                    'return_date', 'status_before_recycle', )

    change_form_template = 'admin/partsapp/change_form_fsm_adm.html'

    # exclude = ('supervisor', 'manager', 'shift', 'return_date',
    #            'status_before_recycle', 'description', )

    # fieldsets = (
    #     (_('Parts'), {
    #         'fields': _fields['Parts']
    #     }),
    #     (_('Recycle'), {
    #         'fields': _fields['Recycle']
    #     }),
    #     (_('Approve'), {
    #         'fields': _fields['Approve']
    #     }),
    #     (_('Engineer Approve'), {
    #         'fields': _fields['Engineer_Approve']
    #     }),
    #     (_('Repair'), {
    #         'fields': _fields['Repair']
    #     })
    # )


    def get_form(self, request, obj=None, **kwargs):
        status = Status.DRAFT
        if obj:
            status = obj.state

        # self.fieldsets = [
        #     (_('Parts'), { 'fields': self._fields['Parts'] }), 
        #     (_('Recycle'), { 'fields': self._fields['Recycle'] }), 
        # ]
        # self.exclude = self._fields['Approve'] + self._fields['Engineer Approve'] + self._fields['Repair']

        self.fieldsets = [ (_(v['group']), {'fields': v['fields']}) for v in self._fields if v['status'] <= status ]
        # self.exclude = ( f for f in v['fields'] for v in self._fields if v['status'] <= status )
            
        return super(PartsRecycleAdmin, self).get_form(request, obj, **kwargs)



    
        
# Register your models here.
admin.site.register(PartsRequest, RequestAdmin)
# admin.site.register(RequestDetail)
admin.site.register(PartsRecycle, PartsRecycleAdmin)
