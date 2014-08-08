
from django.utils.translation import ugettext as _
from partsapp.models import Status


def is_draft_url(request):
    return ('/' + Status.URL_SUFFIX[Status.DRAFT] + '/') in request.path

def is_supervisorapprove_url(request):
    return ('/' + Status.URL_SUFFIX[Status.SUPERVISOR_APPROVE] + '/') in request.path

def is_engineerapprove_url(request):
    return ('/' + Status.URL_SUFFIX[Status.ENGINEER_APPROVE] + '/') in request.path

def is_repair_url(request):
    return ('/' + Status.URL_SUFFIX[Status.REPAIR] + '/') in request.path
    
def is_query_url(request):
    return ('/query/') in request.path


def get_status_url_label(request):
    if is_draft_url(request):
        return Status.LABEL[Status.DRAFT]
    elif is_supervisorapprove_url(request):
        return Status.LABEL[Status.SUPERVISOR_APPROVE]
    elif is_engineerapprove_url(request):
        return Status.LABEL[Status.ENGINEER_APPROVE]
    elif is_repair_url(request):
        return Status.LABEL[Status.REPAIR]
    elif is_query_url(request):
        return _('query')
    else:
        return _('parts recycle')
        
