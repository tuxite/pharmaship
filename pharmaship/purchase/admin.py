# -*- coding: utf-8; -*-
"""Admin views for Purchase application."""
from django.contrib import admin

from pharmaship.purchase import models


class RequisitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'reference', 'port_of_delivery', 'requested_date', 'item_type')
    ordering = ('date_of_creation',)

    class Meta:  # noqa: D106
        ordering = ('date_of_creation', )


admin.site.register(models.Requisition, RequisitionAdmin)
admin.site.register(models.Item)
