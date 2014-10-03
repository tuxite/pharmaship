# -*- coding: utf-8; -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('inventory.views_settings',
    url(r'^$', 'index', name="inventory_settings"),
    # Action for Inventory settings form
    url(r'^application$', 'application', name="application"),
    # Export/import allowances
    url(r'^export$', 'export_data', name="export"),
    #~ url(r'^import$', 'import_data', name="import"),
    # Create/delete locations
    url(r'^location/create$', 'create_location', name="create_location"),
    url(r'^location/delete$', 'delete_location', name="delete_location"),
)
