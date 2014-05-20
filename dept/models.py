# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class Department(models.Model):
    name = models.CharField(_('name'), max_length=40)


class Employee(models.Model):
    user = models.OneToOneField(User)
    department = models.ForeignKey(Department, blank=True, null=True)
    leader = models.ForeignKey('self', blank=True, null=True)
    num = models.CharField(_('number'), max_length=20)

