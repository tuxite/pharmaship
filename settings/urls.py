# -*- coding: utf-8; -*-
import logging

from django.conf.urls import patterns, include, url
from django.conf import settings

SYSTEM_APPS = ['core', 'bootstrapform']

key_patterns = patterns('settings.views',
    url(r'^add$', 'import_key', name="import"),
    url(r'^(?P<key_id>[0-9a-fA-F]{8})/delete$', 'delete_key', name="delete"),
)
                        
urlpatterns = patterns('settings.views',
    url(r'^$', 'index', name="index"),
    # Action and view for general data import
    url(r'^import$', 'import_data', name="import"),
    # Action for PGP Key import
    url(r'^key/', include(key_patterns, namespace="key")),
    # Action for Vessel form
    url(r'^vessel$', 'vessel', name="vessel"),
    # Action for User forms
    url(r'^user$', 'user', name="user"),
)

# Automatically adds settings url from applications
logger = logging.getLogger(__name__)

for application in settings.INSTALLED_APPS:
    if "django" in application or application in SYSTEM_APPS:
        continue
    print "Settings", application

    try:
        urlpatterns += patterns('',
            url(r"^{0}/".format(application), include("{0}.settings_urls".format(application), namespace=application, app_name=application)),
        )
    except ImportError:
        logger.debug ("Application %s does not provides urls" % application)
    except TypeError as e:
        print "Erreur", e
        