# -*- coding: utf-8; -*-
from django.conf.urls import patterns, url, include

requisition_patterns = patterns('purchase.views',
    url(r'^create$', 'create', name="create"),
    url(r'^(?P<requisition_id>\d+)$', 'requisition', name="view"),
    url(r'^(?P<requisition_id>\d+)/status$', 'status', name="status"),
    url(r'^(?P<requisition_id>\d+)/name$', 'edit', name="edit"),
    url(r'^(?P<requisition_id>\d+)/print$', 'pdf_print', name="print"),
    url(r'^(?P<requisition_id>\d+)/delete$', 'delete', name="delete"),
    url(r'^(?P<requisition_id>\d+)/instructions$', 'instructions', name="instructions"),   
    url(r'^(?P<requisition_id>\d+)/auto_add$', 'auto_add', name="auto_add"),
    url(r'^(?P<requisition_id>\d+)/name_search$', 'name_search', name="name_search"),
    # TEST - TO DELETE
    url(r'^(?P<requisition_id>\d+)/test$', 'test', name="test"),
)

item_patterns = patterns('purchase.views',    
    url(r'^(?P<requisition_id>\d+)/add$', 'item_add', name="add"),
    url(r'^(?P<requisition_id>\d+)/item/(?P<item_id>\d+)/delete$', 'item_delete', name="delete"), 
    url(r'^update$', 'item_update', name="update"),  
)

urlpatterns = patterns('purchase.views',
    # General
    url(r'^$', 'index', name="index"),
    # Settings
    url(r'^$', 'index', name="settings"),
    # Requisition
    url(r'requisition/', include(requisition_patterns, namespace="requisition")),
    url(r'item/', include(item_patterns, namespace="item")),
)

