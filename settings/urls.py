# -*- coding: utf-8; -*-
#
# (c) 2013 Association DSM, http://devmaretique.com
#
# This file is part of Pharmaship.
#
# Pharmaship is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# any later version.
#
# Pharmaship is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pharmaship.  If not, see <http://www.gnu.org/licenses/>.
#
# ======================================================================
# Filename:    settings/urls.py
# Description: Urls for Settings application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.2"

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
