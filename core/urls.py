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
# Filename:    core/urls.py
# Description: Urls for Onboard Assistant Core application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2014, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('core.views',
    # General
    url(r'^$', 'index'),
    url(r'^language/(?P<language_code>\w*)', 'set_language', name="language"),
)
urlpatterns += patterns('',
    # Contact
    url(r'^contact$', 'inventory.views_common.contact'),
    )
