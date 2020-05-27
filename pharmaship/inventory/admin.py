# -*- coding: utf-8; -*-
"""Admin views for Inventory application."""
from django.contrib import admin

from mptt.admin import MPTTModelAdmin

import pharmaship.inventory.models


class MoleculeAdmin(admin.ModelAdmin):
    """List view for `Molecule`."""

    list_display = ('name', 'dosage_form', 'composition')
    ordering = ('name',)


class EquipmentAdmin(admin.ModelAdmin):
    """List view for `Equipment`."""

    list_display = ('name', 'packaging', 'remark', 'consumable', 'perishable')
    ordering = ('name',)


class ChildAdmin(admin.ModelAdmin):
    """List view for `Article` and `Medicine`."""

    list_display = ('name', 'parent', 'get_quantity', 'exp_date', 'location')


class GroupAdmin(admin.ModelAdmin):
    """List view for `MoleculeGroup` and `EquipmentGroup`."""

    list_display = ('name', 'order')
    ordering = ('order',)


class QtyTransactionAdmin(admin.ModelAdmin):
    """List view for `QtyTransaction`."""

    list_display = (
        'content_object',
        'content_type',
        'value',
        'transaction_type'
        )
    list_filter = ('content_type',)


class ReqQtyAdmin(admin.ModelAdmin):
    """List view for all required quantity models."""

    list_display = ('base', 'allowance', 'required_quantity')
    ordering = ('base', 'allowance',)
    list_filter = ('allowance',)


class AllowanceAdmin(admin.ModelAdmin):
    """List view for `Allowance`."""

    list_display = ('name', 'author', 'version', 'active')
    ordering = ('name', 'version',)


class GenericReqQtyAdmin(admin.ModelAdmin):
    """List view dedicated to Rescue Bag/First Aid Kit required quantities."""

    list_display = ('base', 'allowance', 'required_quantity')
    list_filter = ('allowance',)


class FirstAidKitItemAdmin(admin.ModelAdmin):
    """List view for items in first aid kits."""

    list_display = ('name', 'exp_date', 'kit')
    list_filter = ('kit',)


class RescueBagAdmin(admin.ModelAdmin):
    """List view for `RescueBag`."""

    list_display = ('name', 'location')


# General
# admin.site.register(pharmaship.inventory.models.Settings)
admin.site.register(pharmaship.inventory.models.Allowance, AllowanceAdmin)
admin.site.register(pharmaship.inventory.models.Tag)
admin.site.register(pharmaship.inventory.models.Location, MPTTModelAdmin)
admin.site.register(pharmaship.inventory.models.QtyTransaction, QtyTransactionAdmin)

# Molecule / Medicine
admin.site.register(pharmaship.inventory.models.MoleculeGroup, GroupAdmin)
admin.site.register(pharmaship.inventory.models.Molecule, MoleculeAdmin)
admin.site.register(pharmaship.inventory.models.MoleculeReqQty, ReqQtyAdmin)
admin.site.register(pharmaship.inventory.models.Medicine, ChildAdmin)

# Equipment / Article
admin.site.register(pharmaship.inventory.models.EquipmentGroup, GroupAdmin)
admin.site.register(pharmaship.inventory.models.Equipment, EquipmentAdmin)
admin.site.register(pharmaship.inventory.models.EquipmentReqQty, ReqQtyAdmin)
admin.site.register(pharmaship.inventory.models.Article, ChildAdmin)

# First Aid Kit
admin.site.register(pharmaship.inventory.models.FirstAidKit)
admin.site.register(pharmaship.inventory.models.FirstAidKitReqQty, GenericReqQtyAdmin)
admin.site.register(pharmaship.inventory.models.FirstAidKitItem, FirstAidKitItemAdmin)

# Rescue Bag
admin.site.register(pharmaship.inventory.models.RescueBag, RescueBagAdmin)
admin.site.register(pharmaship.inventory.models.RescueBagReqQty, GenericReqQtyAdmin)

# Telemedical
admin.site.register(pharmaship.inventory.models.TelemedicalReqQty, ReqQtyAdmin)

# Laboratory
admin.site.register(pharmaship.inventory.models.LaboratoryReqQty, ReqQtyAdmin)
