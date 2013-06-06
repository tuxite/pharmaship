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

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('inventory.views',
    url(r'^$', 'index'),

    # Drug Related
    url(r'^/drug/index', 'drug', name="drug"),
    url(r'^/drug/(?P<drug_id>\d+)/delete$', 'drug_delete', name="drug_delete"),
    url(r'^/drug/(?P<inn_id>\d+)/add$', 'drug_add', name="drug_add"),
    url(r'^/drug/(?P<drug_id>\d+)/change$', 'drug_change', name="drug_change"),
    url(r'^/drug/(?P<drug_id>\d+)/out$', 'drug_out', name="drug_out"),
    url(r'^/drug/(?P<inn_id>\d+)/equivalent$', 'drug_equivalent', name="drug_equivalent"),
    url(r'^/drug/(?P<inn_id>\d+)/remark$', 'drug_remark', name="drug_remark"),
    url(r'^/drug/filter$', 'drug_filter', name="drug_filter"),
    url(r'^/drug/print$', 'drug_print', name="drug_print"),

    # Material Related
    url(r'^/material', 'material', name="material"),
)
