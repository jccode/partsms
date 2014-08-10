
from django import template
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
    
