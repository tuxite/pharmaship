# -*- coding: utf-8; -*-
from django.conf.urls import patterns, url, include

medicine_patterns = patterns('inventory.views_medicine',
    url(r'^$', 'index', name="index"),
    url(r'^print$', 'pdf_print', name="print"),
    url(r'^filter$', 'filter', name="filter"),

    url(r'^(?P<molecule_id>\d+)/add$', 'add', name="add"),
    url(r'^(?P<molecule_id>\d+)/equivalent$', 'equivalent', name="equivalent"),
    url(r'^(?P<molecule_id>\d+)/remark$', 'remark', name="remark"),

    url(r'^(?P<medicine_id>\d+)/delete$', 'delete', name="delete"),
    url(r'^(?P<medicine_id>\d+)/change$', 'change', name="change"),
    url(r'^(?P<medicine_id>\d+)/out$', 'out', name="out"),
)

equipment_patterns = patterns('inventory.views_equipment',
    url(r'^$', 'index', name="index"),
    url(r'^print$', 'pdf_print', name="print"),
    url(r'^filter$', 'filter', name="filter"),

    url(r'^(?P<equipment_id>\d+)/add$', 'add', name="add"),
    url(r'^(?P<equipment_id>\d+)/remark$', 'remark', name="remark"),

    url(r'^(?P<article_id>\d+)/delete$', 'delete', name="delete"),
    url(r'^(?P<article_id>\d+)/change$', 'change', name="change"),
    url(r'^(?P<article_id>\d+)/out$', 'out', name="out"),
)

urlpatterns = patterns('inventory.views_common',
    # General
    url(r'^$', 'index', name="index"),
    url(r'^contact', 'contact'),
    # We use namespaces to add the medicine and equipment related patterns
    url(r'^medicine/', include(medicine_patterns, namespace='medicine')),
    url(r'^equipment/', include(equipment_patterns, namespace='equipment')),
)
