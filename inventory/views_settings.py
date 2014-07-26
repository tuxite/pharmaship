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
# Filename:    inventory/views_settings.py
# Description: Views for Inventory application (settings).
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import ModelForm
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.conf import settings

from django.template.loader import render_to_string

import models, forms

from allowance import create_archive, import_archive

from settings.models import User
from settings.forms import UserForm

from core.views import settings_links, settings_validation

import json

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

    return render_to_response('pharmaship/settings.html', {
                        'user': request.user,
                        'title':_("Settings"),
                        'links': settings_links(),
                        'settingsform': forms.SettingsForm(instance=models.Settings.objects.latest('id')),
                        'locationcreateform' : forms.LocationCreateForm(),
                        'locationdeleteform' : forms.LocationDeleteForm(),
                        },
                        context_instance=RequestContext(request))

@permission_required('inventory.settings.can_change')
def application(request):
    """Validation of the Application form."""
    if request.method == 'POST' and request.is_ajax():
        return settings_validation(request, forms.SettingsForm, models.Settings.objects.latest('id'))

    return HttpResponseNotAllowed(['POST',])

@permission_required('inventory')
def export_data(request):
    """Exports an allowance in a tar.gz archive."""
    if request.method == 'POST' and request.is_ajax(): 
        form = forms.ExportForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            allowance = form.cleaned_data['allowance']
            return create_archive(allowance)
        else:
            return HttpResponseRedirect(reverse('inventory_settings'))
    else:
        return HttpResponseNotAllowed(['POST',])

@permission_required('inventory.location.can_add')
def create_location(request):
    """Creates a new Location for items in Inventory application."""
    if request.method == 'POST' and request.is_ajax(): 
        form = forms.LocationCreateForm(request.POST)
        if form.is_valid():
            primary = form.cleaned_data['primary']
            secondary = form.cleaned_data['secondary']
            # Creation of the instance
            added = models.Location(primary=primary, secondary=secondary)
            added.save()
            # Returning the html element added in order to update the list client-side
            updated_form = render_to_string('html/form.html', {'form': forms.LocationDeleteForm()})
            data = json.dumps({'success':_('Data updated'), 'form': updated_form})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
            data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
            return HttpResponseBadRequest(data, content_type = "application/json")
    else:
        return HttpResponseNotAllowed(['POST',])


@permission_required('inventory.location.can_delete')
def delete_location(request):
    """Deletes selected Location objects for items in Inventory application."""
    if request.method == 'POST' and request.is_ajax():
        form = forms.LocationDeleteForm(request.POST)
        if form.is_valid():
            obj = form.cleaned_data['to_delete']
            # Changing values for objects with location in obj
            default = models.Location.objects.get(pk=1)
            models.Medicine.objects.filter(location__in=obj).update(location = default)
            models.Article.objects.filter(location__in=obj).update(location = default)
            # Get the list of ids to be deleted in order to update the list client-side
            obj_id = []
            for item in obj:
                obj_id.append(item.pk)
            # Delete
            obj.delete()
            # Returning the updated list of locations
            print "OBJ", obj_id

            data = json.dumps({'success':_('Data updated'), 'deleted': obj_id})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
            data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
            return HttpResponseBadRequest(data, content_type = "application/json")
    else:
        return HttpResponseNotAllowed(['POST',])
