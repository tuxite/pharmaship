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
# Filename:    inventory/admin.py
# Description: Admin view configuration for Inventory application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

import models
from django.contrib import admin
from django.forms import CheckboxSelectMultiple


class BaseDrugAdmin(admin.ModelAdmin):
    list_display = ('inn', 'packaging', 'required_quantity')
    form = models.BaseDrugForm

class DrugAdmin(admin.ModelAdmin):
    list_display = ('name', 'basedrug_set', 'get_quantity')

class DrugGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)

class DrugTransactionAdmin(admin.ModelAdmin):
    list_display = ('drug', 'basedrug', 'date')

class DrugQtyTransactionAdmin(admin.ModelAdmin):
    list_display = ('drug', 'value', 'transaction_type')
    
admin.site.register(models.BaseDrug, BaseDrugAdmin)
admin.site.register(models.Drug, DrugAdmin)
admin.site.register(models.DrugGroup, DrugGroupAdmin)
admin.site.register(models.DrugTransaction, DrugTransactionAdmin)
admin.site.register(models.DrugQtyTransaction, DrugQtyTransactionAdmin)
