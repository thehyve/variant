from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic import ListView
from django.contrib.auth import views as auth_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^{{ project_name }}/', include('{{ project_name }}.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^login/$', auth_views.login, {'template_name': 'registration/login.html'}, name="login"),
    url(r'^do_login/$', 'eurreca.views.do_login', name="do_login"),
    url(r'^logout/$', 'eurreca.views.do_logout', name="do_logout"),
    (r'^admin/', include(admin.site.urls)),
    (r'^index/$', 'eurreca.views.index'),
    (r'^search/$', 'eurreca.views.search_view'), 
    (r'^advanced_search/$', 'eurreca.views.advanced_search_view'), 
    (r'^studies/$', 'eurreca.views.study_list'),
	(r'^studies/create/$', 'eurreca.views.study_create'),
    (r'^studies/update/(\d+)$', 'eurreca.views.study_update'),
    (r'^studies/view/(\d+)$', 'eurreca.views.study_view'),
    (r'^studies/remove/(\d+)$', 'eurreca.views.study_remove'),
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

