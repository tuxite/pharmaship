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
# Filename:    purchase/urls.py
# Description: Urls for Purchase application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('purchase.views',
    # General
    url(r'^$', 'index', name="purchase"),
    # Settings
    url(r'^$', 'index', name="purchase_settings"),
    # Requisition
    url(r'^requisition/create$', 'create', name="purchase_req_create"),
    url(r'^requisition/(?P<requisition_id>\d+)$', 'requisition', name="purchase_req_view"),
    url(r'^requisition/(?P<requisition_id>\d+)/status$', 'status', name="purchase_req_status"),
    url(r'^requisition/(?P<requisition_id>\d+)/name$', 'edit', name="purchase_req_edit"),
    url(r'^requisition/(?P<requisition_id>\d+)/print$', 'status', name="purchase_req_print"),
    url(r'^requisition/(?P<requisition_id>\d+)/delete$', 'delete', name="purchase_req_delete"),
    url(r'^requisition/(?P<requisition_id>\d+)/add$', 'item_add', name="purchase_item_add"),
    url(r'^requisition/(?P<requisition_id>\d+)/auto_add$', 'auto_add', name="purchase_auto_add"),
    url(r'^item/(?P<item_id>\d+)+(?P<requisition_id>\d+)/delete$', 'item_delete', name="purchase_item_delete"),
    url(r'^requisition/(?P<requisition_id>\d+)/change$', 'item_change', name="purchase_item_change"),
    url(r'^instructions/(?P<requisition_id>\d+)$', 'instructions', name="purchase_instructions"),
    url(r'^name_search/(?P<requisition_id>\d+)$', 'name_search', name="purchase_name_search"),
    # TEST - TO DELETE
    url(r'^requisition/(?P<requisition_id>\d+)/test$', 'test', name="test"),
)

