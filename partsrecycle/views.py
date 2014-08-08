
from django.template.response import TemplateResponse


def permission_denied_view(request):
    template = 'admin/partsapp/permission_denied.html'
    return TemplateResponse(request, template, {})
    
