import settings

from django.conf.urls.defaults import patterns, include, url
from django.http import HttpResponseRedirect

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', lambda req: HttpResponseRedirect('/pantry/dashboard')),
    url(r'^pantry/', include('core.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        { 'document_root': settings.relative_path_to('static/') }),
)
