import operator
import re
from functools import wraps
from django.contrib import admin
from django import forms
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.contrib.admin.sites import site
from django.contrib.admin.util import quote
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext as _
from fsm_admin.mixins import FSMTransitionMixin
from partsrecycle.models import PartsRecycle, Status
from partsrecycle.views import permission_denied_view
from partsrecycle.utils import statusUrl


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
    """
    ChangeList for parts recycle
    """
    def __init__(self, request, *args):
        self.url_status = statusUrl.get_url_status(request)
        super(PartsRecycleChangeList, self).__init__(request, *args)

    def url_for_result(self, result):
        if self.url_status == -1:
            return super(PartsRecycleChangeList, self).url_for_result(result)
        else:
            pk = getattr(result, self.pk_attname)
            url_suffix = statusUrl.get_url_suffix_by_status(self.url_status)
            url = reverse('admin:%s_%s_change_%s' % (self.opts.app_label, self.opts.model_name, url_suffix),
                          args=(quote(pk), ),
                          current_app=self.model_admin.admin_site.name)
            return url
        
    
class PartsRecycleViewChangeList(ChangeList):
    """
    ChangeList for query view
    """
    def __init__(self, *args):
        super(PartsRecycleViewChangeList, self).__init__(*args)        

    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        url = reverse('admin:%s_%s_change_view' % (self.opts.app_label, self.opts.model_name),
                       args=(quote(pk), ),
                       current_app=self.model_admin.admin_site.name)
        return url
        
        
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
        url_status = statusUrl.get_url_status(request)
        if url_status == statusUrl.STATUS_QUERY:
            status = statusUrl.STATUS_QUERY
        elif obj:
            status = obj.state
        else:
            status = Status.DRAFT
        readonly_fields = reduce(operator.add, [ v['fields'] for v in self._fields if v['status'] < status ], ())
        return readonly_fields

    def get_urls(self):
        """
        my_urls = [
            url(r'^draft/$', self.changelist_view_draft), 
            url(r'^supervisorapprove/$', self.changelist_view_supervisorapprove), 
            url(r'^engineerapprove/$', self.changelist_view_engineerapprove), 
            url(r'^repair/$', self.changelist_view_repair),
            url(r'^query/$', self.changelist_view),
            url(r'query/(.+)/$', self.change_view), 
        ]
        """
        urls = super(PartsRecycleAdmin, self).get_urls()
        url_suffixs = statusUrl.url_suffixs
        info = (self.model._meta.app_label, self.model._meta.model_name)
        my_urls = []
        for url_suffix in url_suffixs:
            my_urls.append(url( r'^'+url_suffix+'/$',
                                getattr(self, 'changelist_view_'+url_suffix), 
                                name='%s_%s_changelist_%s' % (info + (url_suffix,))))
            my_urls.append(url(r'^'+url_suffix+'/(.+)/$',
                               self.change_view,
                               name='%s_%s_change_%s' % (info + (url_suffix,))))            
        # for query view
        # query_url_suffix = statusUrl.get_url_suffix_by_status(statusUrl.STATUS_QUERY)
        # my_urls.append(url(r'^'+query_url_suffix+'/(.+)/$',
        #                    self.change_view,
        #                    name='%s_%s_change_view' % info))
        return my_urls + urls

    def get_list_filter(self, request):
        if statusUrl.get_url_status(request) == statusUrl.STATUS_QUERY:
            return ('state', )
        return None

    def get_actions(self, request):
        if statusUrl.get_url_status(request) != Status.DRAFT:
            return None
        return super(PartsRecycleAdmin, self).get_actions(request)
        
    def get_changelist(self, request, **kwargs):
        # url_status = statusUrl.get_url_status(request)
        # if(url_status == statusUrl.STATUS_QUERY):
        #     return PartsRecycleViewChangeList
        # else:
        #     return super(PartsRecycleAdmin, self).get_changelist(request, **kwargs)
        return PartsRecycleChangeList

    def changelist_view(self, request, extra_context=None):
        extra_context = {}
        extra_context['status'] = statusUrl.get_url_status(request)
        extra_context['STATUS'] = Status
        return super(PartsRecycleAdmin, self).changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = {}
        extra_context['status'] = statusUrl.get_url_status(request)
        extra_context['STATUS'] = Status
        return super(PartsRecycleAdmin, self).change_view(request, object_id, form_url, extra_context)
        
    def get_queryset(self, request):
        qs = super(PartsRecycleAdmin, self).get_queryset(request)
        status = statusUrl.get_url_status(request)
        if(status != -1 and status != statusUrl.STATUS_QUERY):
            return qs.filter(state = status)
        else:
            return qs

    # changelist views
    def changelist_view_draft(self, request, extra_context=None):
        return self.changelist_view(request, extra_context)
        
    def changelist_view_query(self, request, extra_context=None):
        return self.changelist_view(request, extra_context)
        # return PartsRecycleViewChangeList(request, extra_context)
    
    @permisson_required_decorator('partsrecycle.can_approve')
    def changelist_view_supervisorapprove(self, request, extra_context=None):
        return self.changelist_view(request, extra_context)
        
    @permisson_required_decorator('partsrecycle.can_engineer_approve')
    def changelist_view_engineerapprove(self, request, extra_context=None):
        return self.changelist_view(request, extra_context)

    # same as above to view. 
    def changelist_view_repair(self, request, extra_context=None):
        @permission_required('partsrecycle.can_repair', login_url=reverse('permission_denined_view'))
        def _wrapper(request, extra_context):
            return self.changelist_view(request, extra_context)
        return _wrapper(request, extra_context)

        
# Register your models here.
admin.site.register(PartsRecycle, PartsRecycleAdmin)
