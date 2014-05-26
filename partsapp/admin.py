from django.contrib import admin
from django import forms
from partsapp.models import PartsRequest, RequestDetail
from django.utils.translation import ugettext as _


class RequestDetailInlineForm(forms.ModelForm):
    
    class Meta:
        widgets = {
            'remark': forms.TextInput(attrs={'size': 20}), 
        }
    

class RequestDetailInline(admin.TabularInline):
    model = RequestDetail
    form = RequestDetailInlineForm
    extra = 1


class RequestAdmin(admin.ModelAdmin):
    inlines = [RequestDetailInline]

    class Media:
        css = {
            "all": ("partsapp/css/parts_request.css", )
        }
        js = ("partsapp/js/parts_request.js", )
            


# Register your models here.
admin.site.register(PartsRequest, RequestAdmin)
# admin.site.register(RequestDetail)

