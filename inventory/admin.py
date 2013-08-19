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
# Description: Admin view configuration.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.2"

import models
from forms import MoleculeForm, SettingsForm
from django.contrib import admin


class MoleculeAdmin(admin.ModelAdmin):
    list_display = ('name', 'dosage_form', 'composition')
    ordering = ('name',)
    form = MoleculeForm


    class Meta:
        ordering = ('name', )


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'packaging', 'consumable', 'perishable')
    ordering = ('name',)


    class Meta:
        ordering = ('name', )


class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'get_quantity', 'location')


class GroupAdmin(admin.ModelAdmin):
    ordering = ('order',)


class QtyTransactionAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'content_type', 'value', 'transaction_type')


class ReqQtyAdmin(admin.ModelAdmin):
    list_display = ('base', 'allowance', 'required_quantity')
    ordering = ('base', 'allowance',)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('primary', 'secondary')


class RemarkAdmin(admin.ModelAdmin):
    list_display = ('text', 'content_object')

class SettingsAdmin(admin.ModelAdmin):
    form = SettingsForm


# General
admin.site.register(models.Allowance)
admin.site.register(models.Tag)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Remark, RemarkAdmin)
admin.site.register(models.QtyTransaction, QtyTransactionAdmin)
admin.site.register(models.Settings, SettingsAdmin)

# Molecule / Medicine
admin.site.register(models.Molecule, MoleculeAdmin)
admin.site.register(models.Medicine, ChildAdmin)
admin.site.register(models.MoleculeReqQty, ReqQtyAdmin)
admin.site.register(models.MoleculeGroup, GroupAdmin)
# Equipment / Article
admin.site.register(models.Equipment, EquipmentAdmin)
admin.site.register(models.Article, ChildAdmin)
admin.site.register(models.EquipmentGroup, GroupAdmin)
admin.site.register(models.EquipmentReqQty, ReqQtyAdmin)
