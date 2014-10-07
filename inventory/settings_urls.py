# -*- coding: utf-8; -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('inventory.views_settings',
    url(r'^$', 'index', name="index"),
    # Action for Inventory settings form
    url(r'^application$', 'application', name="application"),
    # Export/import allowances
    url(r'^export/(?P<allowance_id>\d+)$', 'export_data', name="export"),
    # Create/delete locations
    url(r'^location/create$', 'create_location', name="create_location"),
    url(r'^location/delete$', 'delete_location', name="delete_location"),
)
