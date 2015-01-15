from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'partsms.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # url(r'^admin/', include(admin.site.urls)),
    url(r'', include(admin.site.urls)),    
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^parts/', include('partsrecycle.urls')),

    (r'^selectable/', include('selectable.urls')),

    # APIs
    url(r'', include('partsrequest.urls')),
)


