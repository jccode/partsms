# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# Create your models here.
  

class Department(models.Model):
    name = models.CharField(_('name'), max_length=40)
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('department')
        verbose_name_plural = _('departments')
        


class Employee(models.Model):
    user = models.OneToOneField(User)
    department = models.ForeignKey(Department, blank=True, null=True, verbose_name=_('department'))
    leader = models.ForeignKey('self', blank=True, null=True, verbose_name=_('leader'))
    num = models.CharField(_('number'), max_length=20)

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _('employee')
        verbose_name_plural = _('employees')

    
