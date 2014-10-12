# -*- coding: utf-8; -*-
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('inventory',),
}

urlpatterns = patterns('',
    # Load urls of Core application
    url(r'^', include('core.urls', namespace="core", app_name="core")),
    
    # Load urls of Inventory application
    url(r'^pharmaship/', include('inventory.urls', namespace='pharmaship', app_name='inventory')),

    # Load urls of Purchase application
    url(r'^purchase/', include('purchase.urls', namespace='purchase', app_name='purchase')),
    
    # Load urls of Settings application
    url(r'^settings/', include('settings.urls', namespace='settings', app_name='settings')),

    # Admin views
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Login views
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'html/login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page':'/'}),
    
    # i18n
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),

)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
