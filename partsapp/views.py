
from django.template.response import TemplateResponse


def my_custom_permission_denied_view(request):
    template = 'admin/partsapp/permission_denied.html'
    return TemplateResponse(request, template, {})
    
