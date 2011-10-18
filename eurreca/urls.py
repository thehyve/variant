from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic import ListView
from eurreca.models import Study

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^{{ project_name }}/', include('{{ project_name }}.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', name="login"),
    url(r'^logout/$', 'eurreca.views.logout_view', name="logout"),
    (r'^admin/', include(admin.site.urls)),
    (r'^index/$', 'eurreca.views.index'),
    (r'^studies/$', 'eurreca.views.study_list'),
	(r'^studies/create/$', 'eurreca.views.study_create'),
    (r'^studies/update/(\d+)$', 'eurreca.views.study_update'),
    (r'^studies/view/(\d+)$', 'eurreca.views.study_view'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': settings.STATIC_ROOT}),
    (r'^$', 'eurreca.views.index'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT}),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.STATIC_ROOT}),
    )

