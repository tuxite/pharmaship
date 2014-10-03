# -*- coding: utf-8; -*-
import models
from django.contrib import admin

class RequisitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'reference', 'port_of_delivery', 'requested_date', 'item_type')
    ordering = ('date_of_creation',)
    

    class Meta:
        ordering = ('date_of_creation', )


admin.site.register(models.Requisition, RequisitionAdmin)
admin.site.register(models.Item)
