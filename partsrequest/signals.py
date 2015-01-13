# -*- coding: utf-8 -*-

from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import date
from partsrequest.models import PartsRequest, RequestDetail
from partsrecycle.models import PartsRecycle


@receiver(post_save, sender=PartsRequest)
def insert_partsrecycle_after_partsrequest_saved(sender, **kwargs):
    """
    Insert parts recycle after parts request saved

    Arguments:
    - `sender`:
    - `**kwargs`:
    """
    pass
    

@receiver(post_save, sender=RequestDetail)
def insert_partsrecycle_after_requestdetail_saved(sender, **kwargs):
    """
    Insert parts recycle after request detail saved
    
    Arguments:
    - `sender`:
    - `**kwargs`:
    """
    if kwargs['created']:
        rd = kwargs['instance']
        actual_qty = rd.actual_qty
        try:
            actual_qty = int(actual_qty)
            if actual_qty > 0:
                for i in range(actual_qty):
                    pr = PartsRecycle()
                    pr.request_no = rd.request
                    pr.parts = rd.description
                    pr.pn = rd.pn
                    pr.save()
        except:
            print "Parse actual quatity of request detail to integer failed"
            
            
       
