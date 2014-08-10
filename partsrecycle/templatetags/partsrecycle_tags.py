
from django import template
from django.template.defaultfilters import stringfilter
from partsrecycle.utils import statusUrl

register = template.Library()

@register.filter
def status_menu_name(status):
    """
    return the menu name of status url

    Arguments:
    - `status`:
    """
    return statusUrl.get_menu_name_by_status(status)
    
@register.filter
def status_urlname(value, arg):
    print '-----'
    print arg
    url_suffix = statusUrl.get_url_suffix_by_status(arg)
    print url_suffix
    return 'admin:%s_%s_changelist_%s' % (value.app_label, value.model_name, url_suffix)
