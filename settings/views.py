# -*- coding: utf-8; -*-
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed

import json

import models, forms
from core.import_data import BaseImport
from core.manage_key import KeyManager
from core.views import settings_links, settings_validation, app_links

@login_required
def index(request):
    """Displays differents forms to configure Pharmaship."""
    return render_to_response('settings.html', {
                        'user': request.user,
                        'title': _("Settings"),
                        'links': settings_links(),
                        'head_links': app_links(request.resolver_match.namespace),
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
        if f.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            import_file = request.FILES['file_obj']
            # Passing the file to the core function
            km = KeyManager()
            log = km.add_key(import_file)
            return log
        else:
            # Returning errors
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

