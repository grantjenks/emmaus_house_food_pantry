import views
import settings

from django.conf.urls.defaults import patterns, include, url
from django.http import HttpResponseRedirect

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', lambda req: HttpResponseRedirect('/inventory/1')),
    url(r'^inventory/(?P<page>\d+)$', views.inventory),
    url(r'^inventory/update$', views.item_update),
    url(r'^inventory/new$', views.item_new),
    url(r'^inventory/label$', views.lookup_label),
    url(r'^inventory/release$', views.item_release),
    url(r'^receiving$', views.receiving),
    url(r'^receipt$', views.receipt),
    url(r'^distribution$', views.distribution),
    url(r'^admin/', include(admin.site.urls)),
)
