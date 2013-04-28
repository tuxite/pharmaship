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
# Filename:    inventory/urls.py
# Description: Urls for Inventory application.
# ======================================================================

__author__ = "Django Project, Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('inventory.views',
    url(r'^$', 'index'),
    url(r'drugs', 'drugs'),
    url(r'material', 'material'),
    
    url(r'^/drug/(?P<drug_id>\d+)/delete$', 'drugs_delete', name="drug_delete"),
    url(r'^/drug/(?P<inn_id>\d+)/add$', 'drugs_add', name="drug_add"),
    url(r'^/drug/(?P<drug_id>\d+)/change$', 'drugs_change', name="drug_change"),
    url(r'^/drug/(?P<inn_id>\d+)/equivalent$', 'drugs_equivalent', name="drug_equivalent"),
)
