# -*- coding: utf-8; -*-
from django.conf.urls import patterns, url, include

location_patterns = patterns('inventory.views_settings',
    url(r'^create$', 'create_location', name="create"),
    url(r'^(?P<location_id>\d+)/delete$', 'delete_location', name="delete"),
)
urlpatterns = patterns('inventory.views_settings',
    url(r'^$', 'index', name="index"),
    # Action for Inventory settings form
    url(r'^application$', 'application', name="application"),
    # Export/import allowances
    url(r'^export/(?P<allowance_id>\d+)$', 'export_data', name="export"),
    # Create/delete locations
    url(r'^location/', include(location_patterns, namespace="location")),
)