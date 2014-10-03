# -*- coding: utf-8; -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('inventory.views_common',
    # General
    url(r'^$', 'index', name="pharmaship"),
    url(r'^contact', 'contact'),
)

urlpatterns += patterns('inventory.views_medicine',
    # Medicine Related
    url(r'^medicine/$', 'index', name="medicine"),
    url(r'^medicine/filter$', 'filter', name="pharmaship_med_filter"),
    url(r'^medicine/print$', 'pdf_print', name="pharmaship_med_print"),

    url(r'^medicine/(?P<molecule_id>\d+)/add$', 'add', name="pharmaship_med_add"),
    url(r'^medicine/(?P<molecule_id>\d+)/equivalent$', 'equivalent', name="pharmaship_med_equivalent"),
    url(r'^medicine/(?P<molecule_id>\d+)/remark$', 'remark', name="pharmaship_med_remark"),

    url(r'^medicine/(?P<medicine_id>\d+)/delete$', 'delete', name="pharmaship_med_delete"),
    url(r'^medicine/(?P<medicine_id>\d+)/change$', 'change', name="pharmaship_med_change"),
    url(r'^medicine/(?P<medicine_id>\d+)/out$', 'out', name="pharmaship_med_out"),

)
urlpatterns += patterns('inventory.views_equipment',
    # Equipment Related
    url(r'^equipment/index', 'index', name="equipment"),
    url(r'^equipment/print$', 'pdf_print', name="pharmaship_equ_print"),
    url(r'^equipment/filter$', 'filter', name="pharmaship_equ_filter"),

    url(r'^equipment/(?P<equipment_id>\d+)/add$', 'add', name="pharmaship_equ_add"),
    url(r'^equipment/(?P<equipment_id>\d+)/remark$', 'remark', name="pharmaship_equ_remark"),

    url(r'^equipment/(?P<article_id>\d+)/delete$', 'delete', name="pharmaship_equ_delete"),
    url(r'^equipment/(?P<article_id>\d+)/change$', 'change', name="pharmaship_equ_change"),
    url(r'^equipment/(?P<article_id>\d+)/out$', 'out', name="pharmaship_equ_out"),

)
