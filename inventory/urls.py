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

    # Medicine Related
    url(r'^/medicine/index', 'medicine', name="medicine"),
    url(r'^/medicine/(?P<medicine_id>\d+)/delete$', 'medicine_delete', name="medicine_delete"),
    url(r'^/medicine/(?P<inn_id>\d+)/add$', 'medicine_add', name="medicine_add"),
    url(r'^/medicine/(?P<medicine_id>\d+)/change$', 'medicine_change', name="medicine_change"),
    url(r'^/medicine/(?P<medicine_id>\d+)/out$', 'medicine_out', name="medicine_out"),
    url(r'^/medicine/(?P<inn_id>\d+)/equivalent$', 'medicine_equivalent', name="medicine_equivalent"),
    url(r'^/medicine/(?P<inn_id>\d+)/remark$', 'medicine_remark', name="medicine_remark"),
    url(r'^/medicine/filter$', 'medicine_filter', name="medicine_filter"),
    url(r'^/medicine/print$', 'medicine_print', name="medicine_print"),

    # Material Related
    url(r'^/material', 'material', name="material"),
)
