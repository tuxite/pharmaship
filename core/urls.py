# -*- coding: utf-8; -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('core.views',
    # General
    url(r'^$', 'index'),
    url(r'^language/(?P<language_code>\w*)', 'set_language', name="language"),
)
urlpatterns += patterns('',
    # Contact
    url(r'^contact$', 'inventory.views_common.contact'),
    )
