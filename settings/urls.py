# -*- coding: utf-8; -*-
import logging

from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('settings.views',
    url(r'^$', 'index', name="settings"),
    # Action and view for general data import
    url(r'^import$', 'import_data', name="import"),
    # Action for PGP Key import
    url(r'^key/add$', 'import_key', name="import_key"),
    url(r'^key/(?P<key_id>[0-9a-fA-F]{8})/delete$', 'delete_key', name="settings_delete_key"),
    # Action for Vessel form
    url(r'^vessel$', 'vessel', name="vessel"),
    # Action for User forms
    url(r'^user$', 'user', name="user"),
)

# Automatically adds settings url from applications
logger = logging.getLogger(__name__)

for application in settings.INSTALLED_APPS:
    try:
        urlpatterns += patterns('',
            (r"^%s/" % application, include("%s.settings_urls" % application)),
        )
    except:
        logger.debug ("Application %s does not provides urls" % application)
