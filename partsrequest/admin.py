
import ast
from django.contrib import admin
from django import forms
from django.contrib.auth import models as auth
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext as _
from partsrequest.models import PartsRequest, RequestDetail
from selectable.forms.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField
from selectable.forms.widgets import AutoCompleteSelectMultipleWidget, AutoComboboxWidget
from dept.models import Employee
from dept.lookups import EmployeeLookup
from dept.utils import user_str


# Register your models here.

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
    def __init__(self, *args, **kwargs):
        if kwargs and 'instance' in kwargs and kwargs['instance']:
            pq = kwargs['instance']
            if pq.approver and "," in pq.approver:
                pq.approver = pq.approver.split(",")
        super(RequestAdminForm, self).__init__(*args, **kwargs)
    
    # approver = forms.ModelMultipleChoiceField(label=_('Approver'),
    #                                           widget=forms.SelectMultiple,
    #                                           queryset=Employee.objects.all())
    employee = AutoCompleteSelectField(lookup_class=EmployeeLookup, allow_new=True, label=_('Employee'))
    # approver = forms.ModelMultipleChoiceField(queryset=Employee.objects.all(), 
    #                                           widget=FilteredSelectMultiple(_("Approver"),
    #                                                                         is_stacked=False),
    #                                           label=_('Approver'))
    # approver = AutoCompleteSelectMultipleField(lookup_class=EmployeeLookup, label=_("Approver"))

    class Meta:
        model = PartsRequest
        exclude = []
        widgets = {
            'approver': AutoCompleteSelectMultipleWidget(lookup_class=EmployeeLookup, position="bottom-inline")
        }
        

class RequestAdmin(admin.ModelAdmin):
    form = RequestAdminForm
    inlines = [RequestDetailInline]
    list_display = ('request_no', 'apply_type', 'material_type', 'request_date', 'apply_reason',
                    'department', 'employee_num',
                    'employee', 'cost_center', 'approver_name',)
    # fields = ('request_no', 'apply_type', 'material_type', 'apply_reason', ('employee', 'employee_num', 'department'),
    #           'cost_center', 'approver', 'request_date')

    def approver_name(self, obj):
        def display_name(uname):
            try:
                u = auth.User.objects.get(username=uname)
                return user_str(u)
            except Exception as e:
                return uname
            
        approver_unames = obj.approver
        approvers = map(display_name, approver_unames.split(','))
        return "[%s]" % (", ".join(approvers))
        # return obj.approver
    approver_name.short_description = _('Approver')

    # def get_form(self, request, obj=None, **kwargs):
    #     if not obj:
    #         return RequestAdminForm
    #     return super(RequestAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.approver = ",".join(ast.literal_eval(obj.approver))
        obj.save()
        
    class Media:
        css = {
            "all": ("partsrequest/css/parts_request.css", "common/css/style.css", )
        }
        js = ("partsrequest/js/parts_request.js", )
        


# Register your models here

admin.site.register(PartsRequest, RequestAdmin)
# admin.site.register(RequestDetail)

