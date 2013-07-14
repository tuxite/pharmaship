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
from forms import MoleculeForm
from django.contrib import admin

class MoleculeAdmin(admin.ModelAdmin):
    list_display = ('name', 'dosage_form', 'composition')
    ordering = ('name',)
    form = MoleculeForm

    class Meta:
        ordering = ('name', )

class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'molecule_set', 'get_quantity', 'location')

class MedicineGroupAdmin(admin.ModelAdmin):
    ordering = ('order',)

class MedicineTransactionAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'molecule', 'date')

class MedicineQtyTransactionAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'value', 'transaction_type')

class MedicineReqQtyAdmin(admin.ModelAdmin):
    list_display = ('inn', 'allowance', 'required_quantity')
    ordering = ('inn', 'allowance',)

class LocationAdmin(admin.ModelAdmin):
    list_display = ('primary', 'secondary')

class RemarkAdmin(admin.ModelAdmin):
    list_display = ('text', 'molecule')
            
admin.site.register(models.Molecule, MoleculeAdmin)
admin.site.register(models.Medicine, MedicineAdmin)
admin.site.register(models.MedicineGroup, MedicineGroupAdmin)
admin.site.register(models.MedicineTransaction, MedicineTransactionAdmin)
admin.site.register(models.MedicineQtyTransaction, MedicineQtyTransactionAdmin)
admin.site.register(models.MedicineReqQty, MedicineReqQtyAdmin)
admin.site.register(models.Allowance)
admin.site.register(models.Tag)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Remark, RemarkAdmin)
