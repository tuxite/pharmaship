# -*- coding: utf-8; -*-
from django.conf.urls import patterns, url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('core.views',
    # General
    url(r'^$', 'index'),
    url(r'^language/(?P<language_code>\w*)', 'set_language', name="language"),
)
urlpatterns += patterns('',
    # Contact
    url(r'^contact$', 'inventory.views_common.contact'),
    )

# Access to the documentation, only in DEBUG mode.
# In production these files must be treated by the server Apache or NGinx.
urlpatterns += static(settings.DOCS_URL, document_root=settings.DOCS_ROOT)
