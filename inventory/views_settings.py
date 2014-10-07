# -*- coding: utf-8; -*-
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed

from django.template.loader import render_to_string

import models, forms

from import_data import create_archive

from core.views import settings_links, settings_validation, app_links

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
                        'head_links': app_links(request.resolver_match.namespace),
                        'links': settings_links(),
                        'settingsform': forms.SettingsForm(instance=models.Settings.objects.latest('id')),
                        'locationcreateform' : forms.LocationCreateForm(),
                        'locations' : models.Location.objects.all().exclude(pk=1),
                        },
                        context_instance=RequestContext(request))

@permission_required('inventory.settings.can_change')
def application(request):
    """Validation of the Application form."""
    if request.method == 'POST' and request.is_ajax():
        return settings_validation(request, forms.SettingsForm, models.Settings.objects.latest('id'))

    return HttpResponseNotAllowed(['POST',])

@permission_required('inventory')
def export_data(request, allowance_id):
    """Exports an allowance in a tar.gz archive."""
    allowance = get_object_or_404(models.Allowance, pk=allowance_id)
    return create_archive(allowance)

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
            content = render_to_response('pharmaship/location.inc.html', {
                    'item': added,
                    }).content 
            data = json.dumps({'success': _('Data updated'), 'location': content})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
            data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
            return HttpResponseBadRequest(data, content_type = "application/json")
    else:
        return HttpResponseNotAllowed(['POST',])


@permission_required('inventory.location.can_delete')
def delete_location(request, location_id):
    """Deletes selected Location objects for items in Inventory application."""
    if location_id == 0:
        data = json.dumps({'error': _('Something went wrong!'), 'details':_("You can't delete this location.")})
        return HttpResponseBadRequest(data, content_type = "application/json")
    
    if request.is_ajax():
        location = get_object_or_404(models.Location, pk=location_id)
        
        # Changing values for objects with location in obj
        default = models.Location.objects.get(pk=1)
        models.Medicine.objects.filter(location=location).update(location = default)
        models.Article.objects.filter(location=location).update(location = default)
        # Delete
        location.delete()
        # Returns the location id deleted to remove it from the DOM
        data = json.dumps({'success':_('Data updated'), 'deleted': location_id})
        return HttpResponse(data, content_type="application/json")
    else:
        return HttpResponseNotAllowed(['GET',])
