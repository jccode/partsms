"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'partsms.dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'partsms.dashboard.CustomAppIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.importlib import import_module
from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name
from partsrecycle.models import Status
from partsrecycle.utils import statusUrl

# Custom module for PartsRecycle
class PartsRecycleModule(modules.DashboardModule, modules.AppListElementMixin):
    """
    Module for PartsRecycle model
    """
    template = 'admin_tools/dashboard/modules/model_list.html'
    models = 'partsrecycle.models.PartsRecycle'
    
    def __init__(self, **kwargs):
        self.title = _('Parts Recycle')
        super(PartsRecycleModule, self).__init__(self.title, **kwargs)
        
    def init_with_context(self, context):
        """
        self.children += [{
            'title': _('Parts Recycle'),
            'change_url': change_url + 'draft/', 
            'add_url': add_url
        }, {
            'title': _('supervisor approve'),
            'change_url': change_url + 'supervisorapprove/'
        }, {
            'title': _('engineer approve'),
            'change_url': change_url + 'engineerapprove/'
        }, {
            'title': _('repaire'),
            'change_url': change_url + 'repair/'
        }, {
            'title': _('query'),
            'change_url': change_url
        }]
        """
        if self._initialized:
            return

        mod, inst_str = self.models.rsplit('.', 1)
        mod = import_module(mod)
        inst = getattr(mod, inst_str)
        app_label, model_name = inst._meta.app_label, inst._meta.model_name
        user = context['request'].user

        info2 = (app_label, model_name)
        url_draft_suffix = statusUrl.get_url_suffix_by_status(Status.DRAFT)
        add_url = reverse('admin:%s_%s_add_%s' % (app_label, model_name, url_draft_suffix))
        
        draft_child = {'title': statusUrl.get_menu_name_by_status(Status.DRAFT)}
        if user.has_perm('%s.add_%s' % info2):
            draft_child['add_url'] = add_url
        if user.has_perm('%s.change_%s' % info2):
            draft_child['change_url'] = reverse('admin:%s_%s_changelist_%s' % (app_label, model_name, url_draft_suffix))
        if 'add_url' in draft_child:
            self.children.append(draft_child)

        perm_dict = {
            Status.SUPERVISOR_APPROVE: '%s.can_approve' % app_label,
            Status.ENGINEER_APPROVE: '%s.can_engineer_approve' % app_label,
            Status.REPAIR: '%s.can_repair' % app_label,
            statusUrl.STATUS_QUERY: '%s.change_%s' % info2
        }
        for status in perm_dict.keys():
            if user.has_perm(perm_dict[status]):
                self.children.append({
                    'title': statusUrl.get_menu_name_by_status(status),
                    'change_url': reverse('admin:%s_%s_changelist_%s' %
                                          (info2 + (statusUrl.get_url_suffix_by_status(status),)))
                })
            
        self._initialized = True


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for partsms.
    """
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        self.children += [
            modules.ModelList(
                title='Administration',
                models=['django.contrib.auth.*', 'dept.*']
            ),

            modules.ModelList(
                title=_('General Parts Request'),
                models=['partsrequest.*'],
            ), 
        ]
        self.children.append(PartsRecycleModule())
        # append a recent actions module
        self.children.append(modules.RecentActions(_('Recent Actions'), 5))


class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for partsms.
    """

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)
        if self.app_title == 'Partsrecycle':
            self.children.append(PartsRecycleModule())
        else:
            self.children.append(modules.ModelList(self.app_title, self.models))
            
        # append a model list module and a recent actions module
        self.children += [
            modules.RecentActions(
                _('Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=5
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboard, self).init_with_context(context)

