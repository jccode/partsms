# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth import models as auth
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMIntegerField, transition
from dept.models import Employee
from partsrequest.models import PartsRequest


# Create your models here.

class Status(object):
    """
    PartsRecycle workflow status
    """
    DRAFT = 0
    SUPERVISOR_APPROVE = 1
    ENGINEER_APPROVE = 2
    REPAIR = 3
    COMPLETED = 4

    CHOICES = (
        (DRAFT, _('draft')),
        (SUPERVISOR_APPROVE, _('supervisor approve')),
        (ENGINEER_APPROVE, _('engineer approve')),
        (REPAIR, _('repaire')),
        (COMPLETED, _('completed')), 
    )
    
SHIFT_CHOICES = (
    ('A', 'Shift A'),
    ('B', 'Shift B'),
    ('C', 'Shift C'), 
)

STATUS_BEFORE_RECYCLE = (
    ('Good', 'Good'),
    ('NG', 'NG'),
    ('Unknow', 'Unknow'), 
)

STATUS_AFTER_REPAIRED = (
    ('Repaied', _('Repaired')),
    ('Scrapped', _('Scrapped')),
    ('Engineering material', _('Engineering material')), 
)

class PartsRecycle(models.Model):
    request_no = models.ForeignKey(PartsRequest, verbose_name=_('Request number'))
    parts = models.CharField(_('Parts'), max_length=100) # ref `RequestDetail.description`
    pn = models.CharField(_('P/N'), max_length=20)
    sn = models.CharField(_('SN'), max_length=30)
    tool = models.CharField(_('Tool'), max_length=20)
    stn = models.CharField(_('STN'), max_length=50)

    # employee = models.ForeignKey(Employee, related_name="+", verbose_name=_('Recycler'), null=True)
    # supervisor = models.ForeignKey(Employee, related_name="+", verbose_name=_('Supervisor'), null=True)
    # manager = models.ForeignKey(Employee, related_name="+", verbose_name=_('Manager'), null=True)
    employee = models.CharField(_('Recycler'), max_length=50, null=True)
    supervisor = models.CharField(_('Supervisor'), max_length=50, null=True)
    manager = models.CharField(_('Manager'), max_length=50, null=True)
    shift = models.CharField(_('Shift'), choices=SHIFT_CHOICES, max_length=3, null=True)
    return_date = models.DateField(_('Return Date'), null=True)
    status_before_recycle = models.CharField(_('Status before recycle'), choices=STATUS_BEFORE_RECYCLE, max_length=20, null=True)
    description = models.TextField(_('Description'), max_length=200, blank=True, null=True)

    # approver = models.ForeignKey(Employee, related_name="+", verbose_name=_('Confirmmer'), null=True)
    approver = models.CharField(_('Confirmmer'), max_length=50, null=True)
    approve_date = models.DateField(_('Approve Date'), null=True)
    confirm_result = models.CharField(_('Confirm result'), max_length=50, null=True)
    remark_approved = models.TextField(_('Remark'), max_length=200, blank=True, null=True)

    # engineer_approver = models.ForeignKey(Employee, related_name="+", verbose_name=_('Confirmmer'), null=True)
    engineer_approver = models.CharField(_('Confirmmer'), max_length=50, null=True)
    engineer_approve_date = models.DateField(_('Approve Date'), null=True)
    repaireable = models.NullBooleanField(_('Repairable'), null=True)
    # engineer_ack_status = models.CharField(_('Status'), choices=STATUS_AFTER_REPAIRED, max_length=20, null=True)
    remark_engineer = models.TextField(_('Remark'), max_length=200, blank=True, null=True)

    # repairer = models.ForeignKey(Employee, related_name="+", verbose_name=_('Repairer'), null=True)
    repairer = models.CharField(_('Repairer'), max_length=50, null=True)
    repair_date = models.DateField(_('Repaired Date'), null=True)
    remark_repairer = models.TextField(_('Remark'), max_length=200, blank=True, null=True)
    status_after_repaired = models.CharField(_('Status after repaired'), choices=STATUS_AFTER_REPAIRED, max_length=20, null=True)

    store_in_date = models.DateField(_('Store Date'), blank=True, null=True)
    store_in_num = models.CharField(_('Store in number'), max_length=20, blank=True, null=True)

    state = FSMIntegerField(default=Status.DRAFT, verbose_name=_('Flow state'), choices=Status.CHOICES, protected=True)
    
    class Meta:
        verbose_name = _('Parts Recycle')
        verbose_name_plural = _('Parts Recycles')
        permissions = [
            ('can_approve', 'Can approve'), 
            ('can_engineer_approve', 'Engineer approve'), 
            ('can_repair', 'Can repair')
        ]

    def __unicode__(self):
        return "%s %s" % (self.parts, self.sn)
        


    # ########################################
    # transition

    @transition(field=state, source=Status.DRAFT, target=Status.SUPERVISOR_APPROVE,
                custom={'button_name':_('Supervisor Approve')})
    def supervisor_approve(self):
        pass

    @transition(field=state, source=Status.SUPERVISOR_APPROVE, target=Status.ENGINEER_APPROVE,
                custom={'button_name':_('Engineer Approve')})
    def engineer_approve(self):
        pass

    @transition(field=state, source=Status.ENGINEER_APPROVE, target=Status.REPAIR,
                custom={'button_name':_('Repair')})
    def repair(self):
        pass

    @transition(field=state, source=Status.ENGINEER_APPROVE, target=Status.COMPLETED,
                custom={'button_name':_('Scrapped')})
    def obsolete(self):
        # value = map(lambda e: e[0], STATUS_AFTER_REPAIRED).index('Scrapped')
        self.status_after_repaired = 'Scrapped'
        
    @transition(field=state, source=Status.REPAIR, target=Status.COMPLETED,
                custom={'button_name':_('Submit')})
    def complete(self):
        pass

