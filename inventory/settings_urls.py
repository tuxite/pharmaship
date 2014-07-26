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
# Filename:    iventory/settings_urls.py
# Description: Urls for the settings of the Inventory application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.2"

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
