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
        if self._initialized:
            return

        mod, inst_str = self.models.rsplit('.', 1)
        model = import_module(mod)
        inst = getattr(model, inst_str)

        add_url = self._get_admin_add_url(inst, context)
        change_url = self._get_admin_change_url(inst, context)
        applist_url = self._get_admin_app_list_url(inst, context)

        user = context['request'].user
        app_label = inst._meta.app_label

        # add children
        draft_dict = {'title': Status.LABEL[Status.DRAFT] }
        if user.has_perm('%s.add_%s' % (app_label, inst_str.lower())):
            draft_dict['add_url'] = add_url
        if user.has_perm('%s.change_%s' % (app_label, inst_str.lower())):
            draft_dict['change_url'] = change_url + Status.URL_SUFFIX[Status.DRAFT]
        if 'add_url' in draft_dict:
            self.children.append(draft_dict)

        if user.has_perm('%s.can_approve' % app_label):
            self.children.append({
                'title': Status.LABEL[Status.SUPERVISOR_APPROVE],
                'change_url': change_url + Status.URL_SUFFIX[Status.SUPERVISOR_APPROVE]
            })

        if user.has_perm('%s.can_engineer_approve' % app_label):
            self.children.append({
                'title': Status.LABEL[Status.ENGINEER_APPROVE],
                'change_url': change_url + Status.URL_SUFFIX[Status.ENGINEER_APPROVE]
            })

        if user.has_perm('%s.can_repair' % app_label):
            self.children.append({
                'title': Status.LABEL[Status.REPAIR],
                'change_url': change_url + Status.URL_SUFFIX[Status.REPAIR]
            })

        if user.has_perm('%s.change_%s' % (app_label, inst_str.lower())):
            self.children.append({
                'title': _('query'),
                'change_url': change_url + "query"
            })
            
        # self.children += [{
        #     'title': _('Parts Recycle'),
        #     'change_url': change_url + 'draft/', 
        #     'add_url': add_url
        # }, {
        #     'title': _('supervisor approve'),
        #     'change_url': change_url + 'supervisorapprove/'
        # }, {
        #     'title': _('engineer approve'),
        #     'change_url': change_url + 'engineerapprove/'
        # }, {
        #     'title': _('repaire'),
        #     'change_url': change_url + 'repair/'
        # }, {
        #     'title': _('query'),
        #     'change_url': change_url
        # }]
        
        self._initialized = True
        


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for partsms.
    """
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        
        # append a link list module for "quick links"
        
        # self.children.append(modules.LinkList(
        #     _('Quick links'),
        #     layout='inline',
        #     draggable=False,
        #     deletable=False,
        #     collapsible=False,
        #     children=[
        #         [_('Return to site'), '/'],
        #         [_('Change password'),
        #          reverse('%s:password_change' % site_name)],
        #         [_('Log out'), reverse('%s:logout' % site_name)],
        #     ]
        # ))

        
        # append a feed module
        
        # self.children.append(modules.Feed(
        #     _('Latest Django News'),
        #     feed_url='http://www.djangoproject.com/rss/weblog/',
        #     limit=5
        # ))

        
        # append another link list module for "support".
        
        # self.children.append(modules.LinkList(
        #     _('Support'),
        #     children=[
        #         {
        #             'title': _('Django documentation'),
        #             'url': 'http://docs.djangoproject.com/',
        #             'external': True,
        #         },
        #         {
        #             'title': _('Django "django-users" mailing list'),
        #             'url': 'http://groups.google.com/group/django-users',
        #             'external': True,
        #         },
        #         {
        #             'title': _('Django irc channel'),
        #             'url': 'irc://irc.freenode.net/django',
        #             'external': True,
        #         },
        #     ]
        # ))

        # append an app list module for "Applications"
        # self.children.append(modules.AppList(
        #     _('Applications'),
        #     exclude=('django.contrib.*',),
        # ))

        # append an app list module for "Administration"
        # self.children.append(modules.AppList(
        #     _('Administration'),
        #     models=('django.contrib.*',),
        # ))

        
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

        # self.children.append(modules.ModelList(
        #     title =  _('Parts Recycle'),
        #     models = ['partsrecycle.models.PartsRecycle'], 
        #     extra = [{
        #         'title': 'confirm parts',
        #         'change_url': 'http://www.baidu.com', 
        #         # 'add_url': 'http://www.sina.com'
        #     }]
        # ))

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
