
from django.template.response import TemplateResponse


def permission_denied_view(request):
    template = 'admin/partsrecycle/permission_denied.html'
    return TemplateResponse(request, template, {})
    
