# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class MyAppConfig(AppConfig):

    name = "partsrequest"
    verbose_name = _("Parts Request")

    def ready(self):
        import partsrequest.signals
        
        
        

