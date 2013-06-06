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
from forms import BaseDrugForm
from django.contrib import admin

class BaseDrugAdmin(admin.ModelAdmin):
    list_display = ('name', 'dosage_form', 'composition')
    ordering = ('name',)
    form = BaseDrugForm

    class Meta:
        ordering = ('name', )

class DrugAdmin(admin.ModelAdmin):
    list_display = ('name', 'basedrug_set', 'get_quantity', 'location')

class DrugGroupAdmin(admin.ModelAdmin):
    ordering = ('order',)

class DrugTransactionAdmin(admin.ModelAdmin):
    list_display = ('drug', 'basedrug', 'date')

class DrugQtyTransactionAdmin(admin.ModelAdmin):
    list_display = ('drug', 'value', 'transaction_type')

class DrugReqQtyAdmin(admin.ModelAdmin):
    list_display = ('inn', 'dotation', 'required_quantity')
    ordering = ('inn', 'dotation',)

class LocationAdmin(admin.ModelAdmin):
    list_display = ('primary', 'secondary')

class RemarkAdmin(admin.ModelAdmin):
    list_display = ('text', 'basedrug')
            
admin.site.register(models.BaseDrug, BaseDrugAdmin)
admin.site.register(models.Drug, DrugAdmin)
admin.site.register(models.DrugGroup, DrugGroupAdmin)
admin.site.register(models.DrugTransaction, DrugTransactionAdmin)
admin.site.register(models.DrugQtyTransaction, DrugQtyTransactionAdmin)
admin.site.register(models.DrugReqQty, DrugReqQtyAdmin)
admin.site.register(models.Dotation)
admin.site.register(models.Tag)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Remark, RemarkAdmin)
