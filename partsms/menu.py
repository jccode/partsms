"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'partsms.menu.CustomMenu'
"""

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.importlib import import_module
from admin_tools.menu import items, Menu
from admin_tools.utils import AppListElementMixin
from partsrecycle.models import Status
from partsrecycle.utils import statusUrl


class PartsRecycleModel(items.MenuItem, AppListElementMixin):
    """
    Parts recycle menu items
    """
    models = 'partsrecycle.models.PartsRecycle'
    
    def __init__(self, title=None, **kwargs):
        self.title = title or _('Partsrecycle')
        mod, inst_str = self.models.rsplit('.', 1)
        mod = import_module(mod)
        inst = getattr(mod, inst_str)
        app_label, model_name = inst._meta.app_label, inst._meta.model_name
        self.app_label = app_label
        self.model_name = model_name
        self.url = reverse('admin:app_list', kwargs={'app_label': self.app_label})
        super(PartsRecycleModel, self).__init__(title, **kwargs)

    def init_with_context(self, context):
        user = context['request'].user        
        info2 = (self.app_label, self.model_name)
        perm_dict = {
            Status.DRAFT: '%s.change_%s' % info2, 
            Status.SUPERVISOR_APPROVE: '%s.can_approve' % self.app_label,
            Status.ENGINEER_APPROVE: '%s.can_engineer_approve' % self.app_label,
            Status.REPAIR: '%s.can_repair' % self.app_label,
            statusUrl.STATUS_QUERY: '%s.change_%s' % info2
        }
        
        for status in perm_dict.keys():
            if user.has_perm(perm_dict[status]):
                self.children.append(items.MenuItem(
                    title = statusUrl.get_menu_name_by_status(status),
                    url = reverse('admin:%s_%s_changelist_%s' %
                                  (info2 + (statusUrl.get_url_suffix_by_status(status),)))
                ))


class CustomMenu(Menu):
    """
    Custom Menu for partsms admin site.
    """
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)


    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        self.children += [
            items.MenuItem(_('Dashboard'), reverse('admin:index')),
            items.Bookmarks(),
            # items.AppList(
            #     _('Applications'),
            #     exclude=('django.contrib.*', 'dept.*', 'partsrecycle.*')
            # ),
        ]

            
        app_menu = items.MenuItem(_('Applications'))
        app_menu.children.append(
            items.ModelList(_('Partsrequest'), ['partsrequest.*'],
                            url=reverse('admin:app_list', kwargs={'app_label': 'partsrequest'}))
        )
        app_menu.children.append(
            PartsRecycleModel()
        )
                                     
        self.children.append(app_menu)
        
        self.children.append(items.AppList(
            _('Administration'),
            models=('django.contrib.*', 'dept.*')
        ))
        return super(CustomMenu, self).init_with_context(context)


        
