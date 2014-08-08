import operator
from functools import wraps
from django.contrib import admin
from django import forms
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.contrib.admin.sites import site
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext as _
from fsm_admin.mixins import FSMTransitionMixin
from partsrecycle.models import PartsRecycle, Status
from partsrecycle.views import permission_denied_view
from partsrecycle import utils


def permisson_required_decorator(perm, login_url=None):
    """
    Helper decorator for permission_required check 
    """
    def real_decorator(func):
        @wraps(func)
        def wrapper(inst, request, extra_context=None, *args, **kwargs):
            permission_denied_url = reverse('permission_denined_view')
            _url = login_url if login_url else permission_denied_url
            @permission_required(perm, login_url=_url)
            def _wrapper(request, extra_context):
                return func(inst, request, extra_context, *args, **kwargs)
            return _wrapper(request, extra_context)
        return wrapper
    return real_decorator


class PartsRecycleChangeList(ChangeList):
    
    def __init__(self, *args):
        super(PartsRecycleChangeList, self).__init__(*args)
        
    def get_queryset(self, request):
        qs = super(PartsRecycleChangeList, self).get_queryset(request)
        
        if utils.is_draft_url(request):
            return qs.filter(state = Status.DRAFT)
        elif utils.is_supervisorapprove_url(request):
            return qs.filter(state = Status.SUPERVISOR_APPROVE)
        elif utils.is_engineerapprove_url(request):
            return qs.filter(state = Status.ENGINEER_APPROVE)
        elif utils.is_repair_url(request):
            return qs.filter(state = Status.REPAIR)
        elif utils.is_query_url(request):
            return qs
        else:
            return qs
        
        
        
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
                    'return_date', 'status_before_recycle', 'state')

    change_form_template = 'admin/partsrecycle/change_form_fsm_adm.html'
    change_list_template = 'admin/partsrecycle/change_list.html'

    def get_form(self, request, obj=None, **kwargs):
        status = Status.DRAFT
        if obj:
            status = obj.state
        self.fieldsets = [ (_(v['group']), {
            # 'classes': ('collapse',),
            'fields': v['fields']
        }) for v in self._fields if v['status'] <= status ]
        return super(PartsRecycleAdmin, self).get_form(request, obj, **kwargs)


    def get_readonly_fields(self, request, obj=None):
        status = Status.DRAFT
        if obj:
            status = obj.state
        readonly_fields = reduce(operator.add, [ v['fields'] for v in self._fields if v['status'] < status ], ())
        return readonly_fields

    def get_urls(self):
        urls = super(PartsRecycleAdmin, self).get_urls()
        my_urls = [
            url(r'^draft/$', self.changlist_view_draft), 
            url(r'^supervisorapprove/$', self.changelist_view_supervisorapprove), 
            url(r'^engineerapprove/$', self.changelist_view_engineer), 
            url(r'^repair/$', self.changelist_view_repair), 
            url(r'^query/$', self.changelist_view),
        ]
        return my_urls + urls

    def get_list_filter(self, request):
        if utils.is_query_url(request):
            pass
        return None
        
        
    # def get_changelist(self, request, **kwargs):
    #     return PartsRecycleChangeList

    def changelist_view(self, request, extra_context=None):
        extra_context = {}
        extra_context['menu_name'] = utils.get_status_url_label(request)
        return super(PartsRecycleAdmin, self).changelist_view(request, extra_context)
        

    def get_queryset(self, request):
        qs = super(PartsRecycleAdmin, self).get_queryset(request)
        
        if utils.is_draft_url(request):
            return qs.filter(state = Status.DRAFT)
        elif utils.is_supervisorapprove_url(request):
            return qs.filter(state = Status.SUPERVISOR_APPROVE)
        elif utils.is_engineerapprove_url(request):
            return qs.filter(state = Status.ENGINEER_APPROVE)
        elif utils.is_repair_url(request):
            return qs.filter(state = Status.REPAIR)
        elif utils.is_query_url(request):
            return qs
        else:
            return qs

    # changelist views
    def changlist_view_draft(self, request, extra_context=None):
        return self.changelist_view(request, extra_context)

    @permisson_required_decorator('partsrecycle.can_approve')
    def changelist_view_supervisorapprove(self, request, extra_context=None):
        return self.changelist_view(request, extra_context)
        
    @permisson_required_decorator('partsrecycle.can_engineer_approve')
    def changelist_view_engineer(self, request, extra_context=None):
        return self.changelist_view(request, extra_context)

    # same as above to view. 
    def changelist_view_repair(self, request, extra_context=None):
        @permission_required('partsrecycle.can_repair', login_url=reverse('permission_denined_view'))
        def _wrapper(request, extra_context):
            return self.changelist_view(request, extra_context)
        return _wrapper(request, extra_context)
        
    
  
    
        
        
# Register your models here.

admin.site.register(PartsRecycle, PartsRecycleAdmin)
