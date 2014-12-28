# -*- coding: utf-8; -*-
import models
from django.contrib import admin


class RankAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority')
    ordering = ('priority',)


    class Meta:
        ordering = ('priority', )

class MouvementAdmin(admin.ModelAdmin):
    list_display = ('date', 'position', 'user')
    ordering = ('date', 'position', 'user')


    class Meta:
        ordering = ('date', 'position', 'user')

admin.site.register(models.Rank, RankAdmin)
admin.site.register(models.Mouvement, MouvementAdmin)
admin.site.register(models.User)
admin.site.register(models.Vessel)
