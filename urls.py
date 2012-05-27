import views
import settings

from django.http import HttpResponseRedirect
from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', lambda req: HttpResponseRedirect('/inventory/1')),
    url(r'^inventory/(?P<page>\d+)$', views.inventory),
    url(r'^inventory/update$', views.item_update),
    url(r'^inventory/new$', views.item_new),
    url(r'^receive$', views.receive),
    url(r'^distribute$', views.distribute),
    url(r'^admin/', include(admin.site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.STATIC_ROOT}),
)
