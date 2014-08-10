
from django.utils.translation import ugettext as _
from partsrecycle.models import Status


class StatusURL(object):

    STATUS_QUERY = 9
    status_url_mappings = [
        {
            'status': Status.DRAFT, 
            'menu_name': _('parts recycle'),
            'url_suffix': 'draft'
        },
        {
            'status': Status.SUPERVISOR_APPROVE, 
            'menu_name': _('supervisor approve'),
            'url_suffix': 'supervisorapprove'
        },
        {
            'status': Status.ENGINEER_APPROVE, 
            'menu_name': _('engineer approve'),
            'url_suffix': 'engineerapprove'
        },
        {
            'status': Status.REPAIR, 
            'menu_name': _('repaire'),
            'url_suffix': 'repair'
        },
        {
            'status': STATUS_QUERY, 
            'menu_name': _('query'),
            'url_suffix': 'query'
        }
    ]
    
    def __init__(self, ):
        self.status = map(lambda i: i['status'], self.status_url_mappings)
        self.url_suffixs = map(lambda i: i['url_suffix'], self.status_url_mappings)

    def get_url_status(self, request):
        """
        Return current status by check current url. 
        if current url is a status url, then return the status it represented.
        else, return -1
        
        Arguments:
        - `self`:
        - `request`:
        """
        curr_url = request.path
        for st in self.status_url_mappings:
            if ('/' + st['url_suffix'] + '/') in curr_url:
                return st['status']
        return -1

    def _get_sturl_item_by_status(self, status):
        """
        Get status item by status

        Arguments:
        - `self`:
        - `status`:
        """
        return filter(lambda i: i['status'] == status, self.status_url_mappings)[0]

    def get_url_menu_name(self, request):
        """
        Get menu name if current url is a status url. if not true, return None

        Arguments:
        - `request`:
        """
        status = self.get_url_status(request)
        if status == -1:
            return None
        else:
            return self._get_sturl_item_by_status(status)['menu_name']


statusUrl = StatusURL()

