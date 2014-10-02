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
# Filename:    settings/views.py
# Description: Views for Settings application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed

import json

import models, forms
from core.import_data import BaseImport
from core.manage_key import KeyManager
from core.views import settings_links, settings_validation

FUNCTIONS = (
		(u'00', "Captain"),
		(u'10', "Chief Officer"),
		(u'11', "Deck Officer"),
		(u'20', "Chief Engineer"),
		(u'21', "Engineer"),
		(u'99', "Ratings"),
	)

@login_required
def index(request):
    """Displays differents forms to configure Pharmaship."""
    return render_to_response('settings.html', {
                        'user': request.user,
                        'title': _("Settings"),
                        'links': settings_links(),
                        'vesselform': forms.VesselForm(instance = models.Vessel.objects.latest('id')),
                        'userform': forms.UserForm(instance = models.User.objects.get(id = request.user.id)),
                        },
                        context_instance=RequestContext(request))

@login_required
def import_data(request):
    """Displays a form to import data to Onboard Assistant."""
    if request.method == 'POST' and request.is_ajax():
        f = forms.ImportForm(request.POST, request.FILES) # A form bound to the POST data
        if f.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            import_file = request.FILES['file_obj']
            # Passing the file to the core function
            importation = BaseImport(import_file)
            log = importation.launch()
            return log
        else:
            # Returning errors
            errors = dict([(k, [unicode(e) for e in v]) for k,v in f.errors.items()])
            data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
            return HttpResponseBadRequest(data, content_type = "application/json")
    
    km = KeyManager()
    return render_to_response('settings/import.html', {
                        'user': request.user,
                        'title': _("Import"),
                        'importform': forms.ImportForm,
                        'importkeyform': forms.ImportKeyForm,
                        'links': settings_links(),
                        'key_list': km.key_list(),
                        },
                        context_instance=RequestContext(request))

@login_required
def import_key(request):
    """Displays a form to import a PGP key to Onboard Assistant."""
    if request.method == 'POST' and request.is_ajax():
        f = forms.ImportKeyForm(request.POST, request.FILES) # A form bound to the POST data
        print f
        if f.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            import_file = request.FILES['file_obj']
            # Passing the file to the core function
            km = KeyManager()
            log = km.add_key(import_file)
            return log
        else:
            # Returning errors
            print "ERROR", request
            errors = dict([(k, [unicode(e) for e in v]) for k,v in f.errors.items()])
            data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
            return HttpResponseBadRequest(data, content_type = "application/json")
    
    return HttpResponseNotAllowed(['POST',])
    
@login_required
def delete_key(request, key_id):
    """Deletes a trusted key from the keyring."""
    if request.is_ajax():
        km = KeyManager()
        log = km.delete_key(key_id)
        return log
    return HttpResponseNotAllowed(['POST',])
        
@permission_required('settings.user_profile.can_change')
def user(request):
    """Validation of the User form."""
    if request.method == 'POST' and request.is_ajax():
        return settings_validation(request, forms.UserForm, models.User.objects.get(id=request.user.id))

    return HttpResponseNotAllowed(['POST',])

@permission_required('settings.vessel.can_change')
def vessel(request):
    """Validation of the Vessel form."""
    if request.method == 'POST' and request.is_ajax():
        return settings_validation(request, forms.VesselForm, models.Vessel.objects.latest('id'))

    return HttpResponseNotAllowed(['POST',])

