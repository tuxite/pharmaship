# -*- coding: utf-8; -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('purchase.views',
    # General
    url(r'^$', 'index', name="purchase"),
    # Settings
    url(r'^$', 'index', name="purchase_settings"),
    # Requisition
    url(r'^requisition/create$', 'create', name="purchase_req_create"),
    url(r'^requisition/(?P<requisition_id>\d+)$', 'requisition', name="purchase_req_view"),
    url(r'^requisition/(?P<requisition_id>\d+)/status$', 'status', name="purchase_req_status"),
    url(r'^requisition/(?P<requisition_id>\d+)/name$', 'edit', name="purchase_req_edit"),
    url(r'^requisition/(?P<requisition_id>\d+)/print$', 'pdf_print', name="purchase_req_print"),
    url(r'^requisition/(?P<requisition_id>\d+)/delete$', 'delete', name="purchase_req_delete"),
    url(r'^requisition/(?P<requisition_id>\d+)/add$', 'item_add', name="purchase_item_add"),
    url(r'^requisition/(?P<requisition_id>\d+)/auto_add$', 'auto_add', name="purchase_auto_add"),
    url(r'^item/(?P<item_id>\d+)+(?P<requisition_id>\d+)/delete$', 'item_delete', name="purchase_item_delete"),
    url(r'^instructions/(?P<requisition_id>\d+)$', 'instructions', name="purchase_instructions"),
    url(r'^name_search/(?P<requisition_id>\d+)$', 'name_search', name="purchase_name_search"),
    url(r'^item/update$', 'item_update', name="purchase_item_update"),
    # TEST - TO DELETE
    url(r'^requisition/(?P<requisition_id>\d+)/test$', 'test', name="test"),
)

