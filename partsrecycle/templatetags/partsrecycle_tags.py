
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
    url_suffix = statusUrl.get_url_suffix_by_status(arg)
    return 'admin:%s_%s_changelist_%s' % (value.app_label, value.model_name, url_suffix)

@register.filter
def status_urlname(value, arg):
    if arg == -1:
        return value
    else:
        url_suffix = statusUrl.get_url_suffix_by_status(arg)
        return value + "_" + url_suffix
    
