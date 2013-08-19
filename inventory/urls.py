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

urlpatterns = patterns('inventory.views_common',
    # General
    url(r'^$', 'index'),
    url(r'^contact', 'contact'),
)

urlpatterns += patterns('inventory.views_medicine',
    # Medicine Related
    url(r'^medicine/$', 'index', name="medicine"),
    url(r'^medicine/filter$', 'filter', name="med_filter"),
    url(r'^medicine/print$', 'pdf_print', name="med_print"),

    url(r'^medicine/(?P<molecule_id>\d+)/add$', 'add', name="med_add"),
    url(r'^medicine/(?P<molecule_id>\d+)/equivalent$', 'equivalent', name="med_equivalent"),
    url(r'^medicine/(?P<molecule_id>\d+)/remark$', 'remark', name="med_remark"),

    url(r'^medicine/(?P<medicine_id>\d+)/delete$', 'delete', name="med_delete"),
    url(r'^medicine/(?P<medicine_id>\d+)/change$', 'change', name="med_change"),
    url(r'^medicine/(?P<medicine_id>\d+)/out$', 'out', name="med_out"),

)
urlpatterns += patterns('inventory.views_equipment',
    # Equipment Related
    url(r'^equipment/index', 'index', name="equipment"),
    url(r'^equipment/print$', 'pdf_print', name="equ_print"),
    url(r'^equipment/filter$', 'filter', name="equ_filter"),

    url(r'^equipment/(?P<equipment_id>\d+)/add$', 'add', name="equ_add"),
    url(r'^equipment/(?P<equipment_id>\d+)/remark$', 'remark', name="equ_remark"),

    url(r'^equipment/(?P<article_id>\d+)/delete$', 'delete', name="equ_delete"),
    url(r'^equipment/(?P<article_id>\d+)/change$', 'change', name="equ_change"),
    url(r'^equipment/(?P<article_id>\d+)/out$', 'out', name="equ_out"),

)
