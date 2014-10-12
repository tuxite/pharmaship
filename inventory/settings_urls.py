# -*- coding: utf-8; -*-
from django.conf.urls import patterns, url, include

location_patterns = patterns('inventory.views_settings',
    url(r'^create$', 'create_location', name="create"),
    url(r'^(?P<location_id>\d+)/delete$', 'delete_location', name="delete"),
)

allowance_patterns = patterns('inventory.views_settings',
    url(r'^(?P<allowance_id>\d+)/enable$', 'allowance_toggle', kwargs={'active': True}, name="enable"),
    url(r'^(?P<allowance_id>\d+)/disable$', 'allowance_toggle', kwargs={'active': False}, name="disable"),
)

urlpatterns = patterns('inventory.views_settings',
    url(r'^$', 'index', name="index"),
    # Action for Inventory settings form
    url(r'^application$', 'application', name="application"),
    # Action to enable or disable one allowance
    url(r'^allowance/', include(allowance_patterns, namespace="allowance")),
    # Export/import allowances
    url(r'^export/(?P<allowance_id>\d+)$', 'export_data', name="export"),
    # Create/delete locations
    url(r'^location/', include(location_patterns, namespace="location")),
)