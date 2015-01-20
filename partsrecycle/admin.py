import operator
import re
from functools import wraps
from django.contrib import admin
from django.contrib import messages
from django import forms
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.contrib.admin.sites import site
from django.contrib.admin.util import quote
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import permission_required
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from fsm_admin.mixins import FSMTransitionMixin
from partsrecycle.models import PartsRecycle, Status
from partsrecycle.views import permission_denied_view
from partsrecycle.utils import statusUrl
from selectable.forms.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField
from selectable.forms.widgets import AutoCompleteSelectWidget
from dept.models import Employee
from dept.lookups import EmployeeLookup


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

            
class PartsRecycleForm(forms.ModelForm):
    employee = AutoCompleteSelectField(lookup_class=EmployeeLookup, allow_new=True, label=_('Recycler'), required=False)
    supervisor = AutoCompleteSelectField(lookup_class=EmployeeLookup, allow_new=True, label=_('Supervisor'), required=False)
    manager = AutoCompleteSelectField(lookup_class=EmployeeLookup, allow_new=True, label=_('Manager'), required=False)
    approver = AutoCompleteSelectField(lookup_class=EmployeeLookup, allow_new=True, label=_('Confirmmer'), required=False)
    engineer_approver = AutoCompleteSelectField(lookup_class=EmployeeLookup, allow_new=True, label=_('Confirmmer'), required=False)
    repairer = AutoCompleteSelectField(lookup_class=EmployeeLookup, allow_new=True, label=_('Repairer'), required=False)

    _required_fields = {
        Status.DRAFT: ('employee', 'supervisor', 'manager'),
        Status.SUPERVISOR_APPROVE: ('approver', ),
        Status.ENGINEER_APPROVE: ('engineer_approver', ),
        Status.REPAIR: ('repairer', )
    }

    def __init__(self, *args, **kwargs):
        super(PartsRecycleForm, self).__init__(*args, **kwargs)
        if kwargs is not None and 'instance' in kwargs and kwargs['instance'] is not None:
            model = kwargs['instance']
            fields = self._required_fields.get(model.state)
            if fields:
                for field in fields:
                    self.fields.get(field).required = True
        else:                   # DRAFT
            for field in self._required_fields.get(Status.DRAFT):
                self.fields.get(field).required = True
        

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
                       'remark_engineer'), 
        }, 
        {
            'group': 'Repair', 
            'status': Status.REPAIR, 
            'fields': ('repairer', 'repair_date', 'remark_repairer', 'status_after_repaired',
                       'store_in_date', 'store_in_num')
        }
    ]

    change_form_template = 'admin/partsrecycle/change_form.html'
    change_list_template = 'admin/partsrecycle/change_list.html'
    form = PartsRecycleForm

    def get_form(self, request, obj=None, **kwargs):
        status = Status.DRAFT
        if obj:
            status = obj.state

        self.fieldsets = [ (_(v['group']), {
            # 'classes': ('collapse',),
            'fields': v['fields']
        }) for v in self._fields if v['status'] <= status ]

        # kwargs = {} if not kwargs else kwargs
        # kwargs['widgets'] = {
        #     "employee":  AutoCompleteSelectWidget(lookup_class=EmployeeLookup, allow_new=True),
        #     "supervisor":  AutoCompleteSelectWidget(lookup_class=EmployeeLookup, allow_new=True),
        #     "manager":  AutoCompleteSelectWidget(lookup_class=EmployeeLookup, allow_new=True),
        #     "approver":  AutoCompleteSelectWidget(lookup_class=EmployeeLookup, allow_new=True),
        #     "engineer_approve":  AutoCompleteSelectWidget(lookup_class=EmployeeLookup, allow_new=True),
        #     "repairer":  AutoCompleteSelectWidget(lookup_class=EmployeeLookup, allow_new=True)
        # }
        
        return super(PartsRecycleAdmin, self).get_form(request, obj, **kwargs)
        # return PartsRecycleForm

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

        draft_url_suffix = statusUrl.get_url_suffix_by_status(Status.DRAFT)
        my_urls.append(url(r'^'+draft_url_suffix+'/add/$',
                           self.add_view,
                           name='%s_%s_add_%s' % (info + (draft_url_suffix,))))
        
        for url_suffix in url_suffixs:
            info2 = (info + (url_suffix,))
            my_urls.append(url(r'^'+url_suffix+'/$',
                               getattr(self, 'changelist_view_'+url_suffix), 
                               name='%s_%s_changelist_%s' % info2))
            my_urls.append(url(r'^'+url_suffix+'/(.+)/history/$',
                               self.history_view,
                               name='%s_%s_history_%s' % info2))            
            my_urls.append(url(r'^'+url_suffix+'/(.+)/$',
                               self.change_view,
                               name='%s_%s_change_%s' % info2))
            
        return my_urls + urls

    def get_list_filter(self, request):
        if statusUrl.get_url_status(request) == statusUrl.STATUS_QUERY:
            return ('state', )
        return None

    def get_list_display(self, request):
        fields = ('request_no', 'parts', 'pn', 'sn', 'tool', 'stn', 'employee', 'shift',
                    'return_date', 'state')
        if statusUrl.get_url_status(request) == statusUrl.STATUS_QUERY:
            return fields + ('status_after_repaired',)
        return fields
        
    def get_actions(self, request):
        if statusUrl.get_url_status(request) != Status.DRAFT:
            return None
        return super(PartsRecycleAdmin, self).get_actions(request)
        
    def get_changelist(self, request, **kwargs):
        return PartsRecycleChangeList

    def _populate_status_to_extra_context(self, request, extra_context=None):
        if extra_context == None:
            extra_context = {}
        extra_context['status'] = statusUrl.get_url_status(request)
        extra_context['STATUS'] = Status
        return extra_context

    def changelist_view(self, request, extra_context=None):
        extra_context = self._populate_status_to_extra_context(request, extra_context)
        return super(PartsRecycleAdmin, self).changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = self._populate_status_to_extra_context(request, extra_context)
        return super(PartsRecycleAdmin, self).change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = self._populate_status_to_extra_context(request, extra_context)
        return super(PartsRecycleAdmin, self).add_view(request, form_url, extra_context)

    def history_view(self, request, object_id, extra_context=None):
        extra_context = self._populate_status_to_extra_context(request, extra_context)
        return super(PartsRecycleAdmin, self).history_view(request, object_id, extra_context)
        
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

    # redirect url
    def get_redirect_url(self, request, obj):
        """
        adjust redirect when fsm_admin button clicked
        """
        opts = self.model._meta
        status = statusUrl.get_url_status(request)
        if self.has_change_permission(request, None):
            if status == -1:
                post_url = reverse('admin:%s_%s_changelist' %
                                   (opts.app_label, opts.model_name, ),
                                   current_app=self.admin_site.name)
            else:
                url_suffix = statusUrl.get_url_suffix_by_status(status)
                post_url = reverse('admin:%s_%s_changelist_%s' %
                                   (opts.app_label, opts.model_name, url_suffix),
                                   current_app=self.admin_site.name)
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, post_url)
        else:
            post_url = reverse('admin:index',
                               current_app=self.admin_site.name)
        return post_url
        
    def response_post_save_add(self, request, obj):
        """
        Override response_post_save_add
        """
        return HttpResponseRedirect(self.get_redirect_url(request, obj))

    def response_post_save_change(self, request, obj):
        """
        Override response_post_save_change
        """
        return HttpResponseRedirect(self.get_redirect_url(request, obj))

    def response_add(self, request, obj, post_url_continue=None):
        """
        Override response_add. for 'continue' button when add a new object
        """
        if post_url_continue == None:
            status = statusUrl.get_url_status(request)
            url_suffix = statusUrl.get_url_suffix_by_status(status) if status != -1 else None
            opts = obj._meta
            pk_value = obj._get_pk_val()

            url_name = 'admin:%s_%s_change' % (opts.app_label, opts.model_name) \
                       if status == -1 else \
                          'admin:%s_%s_change_%s' % (opts.app_label, opts.model_name, url_suffix)
            # if status == -1:
            #     post_url_continue = reverse('admin:%s_%s_change' %
            #                                 (opts.app_label, opts.model_name),
            #                                 args=(pk_value,),
            #                                 current_app=self.admin_site.name)
            # else:
            #     url_suffix = statusUrl.get_url_suffix_by_status(status)
            #     post_url_continue = reverse('admin:%s_%s_change_%s' %
            #                                 (opts.app_label, opts.model_name, url_suffix),
            #                                 args=(pk_value,),
            #                                 current_app=self.admin_site.name)
            post_url_continue = reverse(url_name,
                                        args=(pk_value,),
                                        current_app=self.admin_site.name)            
        return super(PartsRecycleAdmin, self).response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        """
        Override FSMTransitionMixin response_change() function. 
        To handle '_saveasnew' & '_addanother' button redirection
        """
        opts = self.model._meta
        pk_value = obj._get_pk_val()
        preserved_filters = self.get_preserved_filters(request)
        msg_dict = {'name': force_text(opts.verbose_name), 'obj': force_text(obj)}

        status = statusUrl.get_url_status(request)
        url_suffix = statusUrl.get_url_suffix_by_status(status) if status != -1 else None
        
        if '_partsrecycle_saveasnew' in request.POST:
            msg = _('The %(name)s "%(obj)s" was added successfully. You may edit it again below.') % msg_dict
            self.message_user(request, msg, messages.SUCCESS)
            url_name = 'admin:%s_%s_change' % (opts.app_label, opts.model_name) \
                       if status == -1 else \
                          'admin:%s_%s_change_%s' % (opts.app_label, opts.model_name, url_suffix)
            redirect_url = reverse(url_name,
                                   args=(pk_value,),
                                   current_app=self.admin_site.name)
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)
            
        elif '_partsrecycle_addanother' in request.POST:
            msg = _('The %(name)s "%(obj)s" was changed successfully. You may add another %(name)s below.') % msg_dict
            self.message_user(request, msg, messages.SUCCESS)
            url_name = 'admin:%s_%s_add' % (opts.app_label, opts.model_name) \
                       if status == -1 else \
                          'admin:%s_%s_add_%s' % (opts.app_label, opts.model_name, url_suffix)
            redirect_url = reverse(url_name,
                                   current_app=self.admin_site.name)
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)
            
        else:
            return super(PartsRecycleAdmin, self).response_change(request, obj)

    class Media:
        css = {
            "all": ("common/css/style.css", )
        }
        js = ("partsrecycle/js/parts_recycle.js", )

        
# Register your models here.
admin.site.register(PartsRecycle, PartsRecycleAdmin)






