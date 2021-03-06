# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from dept.models import Employee


# Create your models here.

class PartsRequest(models.Model):
    request_no = models.CharField(_('Request number'), primary_key=True, max_length=20)
    apply_type = models.CharField(_('Apply type'), max_length=50)
    material_type = models.CharField(_('Material type'), max_length=50)
    apply_reason = models.CharField(_('Apply reason'), max_length=200)
    # employee = models.ForeignKey(Employee, related_name="+", verbose_name=_('Employee'))
    employee = models.CharField(_('Employee'), max_length=50)
    employee_num = models.CharField(_('Employee number'), max_length=20)
    department = models.CharField(_("Department"), max_length=50)
    cost_center = models.CharField(_('Cost center'), max_length=20)
    # department =   # TODO: ForeignKey -> Department
    # TODO: approver 会有多个人. 多人选择控件. 但不存在外键关联
    approver = models.CharField(_('Approver'), max_length=200)
    request_date = models.DateTimeField(_('Request Date'), default=datetime.now())

    def __unicode__(self):
        return self.request_no

    class Meta:
        verbose_name = _('General Parts Request')
        verbose_name_plural = _('General Parts Requests')

class RequestDetail(models.Model):
    request = models.ForeignKey(PartsRequest)
    pn = models.CharField(_('P/N'), max_length=20)
    bin = models.CharField(_('Bin'), max_length=50)
    description = models.CharField(_('Parts name'), max_length=100)
    qty = models.IntegerField(_('Quantity'))
    actual_qty = models.IntegerField(_('Actual Qty') , blank=True, null=True)
    unit = models.CharField(_('Unit'), max_length=20)
    over_plan_usage = models.IntegerField(_('Over Plan Usage'), blank=True, null=True)
    balance = models.DecimalField(_('Balance'), max_digits=12, decimal_places=2)
    usage_by_once = models.IntegerField(_('Usage by once'), blank=True, null=True)
    remark = models.TextField(_('Remark'), max_length=200, blank=True, null=True)

 
