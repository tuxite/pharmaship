# -*- coding: utf-8; -*-
#
# (c) 2013 Association DSM, http://devmaretique.com
#
# This file is part of Pharmaship.
#
# Pharmaship is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# any later version.
#
# Pharmaship is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pharmaship.  If not, see <http://www.gnu.org/licenses/>.
#
# ======================================================================
# Filename:    core/views.py
# Description: Views for Core application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2014, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.utils import translation
from django.conf import settings

import json

SYSTEM_APPS = ['core', 'bootstrapform']

def settings_links():
    """Returns a list of links for settings views."""
    links = []
    for application in settings.INSTALLED_APPS:
        print "Application:", application
        # Do not take in account Django's applications
        if "django" in application or application in SYSTEM_APPS:
            continue
        app_data = {}
        # By default, adding the general settings application to the dict
        if application == "settings":
            links.append({
                'name': _("Settings"),
                'url': 'settings',
                'active': True
            })  
        # Looking if the applications has settings that can be imported
        elif globals().get("{0}.settings_urls".format(application), True):
            print "MM", application
            links.append({
                'name': _(application.capitalize()),
                'url': "{0}_settings".format(application),
            })              
        else:
            continue
        
    links.append({'name': _('Import'), 'url': 'import'})
    return links

@permission_required('settings')
def settings_validation(request, form, instance=None):
    """Validates the form in args."""
    f = form(request.POST, instance=instance)
    if f.is_valid(): # All validation rules pass
        f.save()
        # Returning nothing
        data = json.dumps({'success':_('Data updated')})
        return HttpResponse(data, content_type="application/json")
    else:
        errors = dict([(k, [unicode(e) for e in v]) for k,v in f.errors.items()])
        data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
        return HttpResponseBadRequest(data, content_type = "application/json")

@login_required
def index(request):
    """Default view. Displays an overview of the requisitions."""

    return render_to_response('core/index.html', {
                    'user': request.user,
                    'title': _("Requisition Overview"),
                    'requisition_list': models.Requisition.objects.all(),
                    },
                    context_instance=RequestContext(request))

@login_required
def set_language(request, language_code):
    if translation.check_for_language(language_code):
        if hasattr(request, 'session'):
                request.session['django_language'] = language_code
        else:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language_code)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseBadRequest("Language code ({0}) unknown.".format(language_code), content_type="application/json")
