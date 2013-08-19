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
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

import models, forms

from allowance import create_archive, import_archive

from django.contrib.auth.models import User
from users.models import UserProfile
from users.forms import UserForm, UserProfileForm

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
    links = []
    for application in settings.INSTALLED_APPS:
        # Do not take in account Django's applications
        if "django" in application:
            continue
        app_data = {}
        # By default, adding the general settings application to the dict
        if application == "settings":
            app_data['name'] = _("Settings")
            app_data['url'] = "settings"
        # Looking if the applications has settings that can be imported
        elif globals().get("{0}.settings.urls".format(application), True):
            print "application"
            app_data['name'] = _(application.capitalize())
            app_data['url'] = "{0}_settings".format(application)
        else:
            continue

        # Set the link as active. NEED IMPROVEMENT.
        if application == "inventory":
            app_data['active'] = True

        links.append(app_data)

    return render_to_response('pharmaship/settings.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'rank': request.user.profile.get_rank(),
                        'title':_("Settings"),
                        'links': links,
                        'settingsform': forms.SettingsForm(instance=models.Settings.objects.latest('id')).as_table(),
                        'exportform': forms.ExportForm().as_table(),
                        'importform': forms.ImportForm().as_table(),
                        'locationcreateform' : forms.LocationCreateForm().as_table(),
                        'locationdeleteform' : forms.LocationDeleteForm().as_table(),
                        },
                        context_instance=RequestContext(request))

@permission_required('inventory')
def validation(request, form, instance=None):
    """Validates the form in args."""
    f = form(request.POST, instance=instance)
    if f.is_valid(): # All validation rules pass
        f.save()
    else:
        # TODO: Error message
        return False

@permission_required('inventory.settings.can_change')
def application(request):
    """Validation of the Application form."""
    if request.method == 'POST':
        validation(request, forms.SettingsForm, models.Settings.objects.latest('id'))

    return HttpResponseRedirect(reverse('inventory_settings')) # Redirect after POST

@permission_required('inventory')
def export_data(request):
    """Exports an allowance in a tar.gz archive."""
    if request.method == 'POST': # If the form has been submitted
        form = forms.ExportForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            allowance = form.cleaned_data['allowance']
            return create_archive(allowance)
        else:
            return HttpResponseRedirect(reverse('inventory_settings'))
    else:
        return HttpResponseRedirect(reverse('inventory_settings'))

@permission_required('inventory.settings.can_change')
def import_data(request):
    """Import data and do some checks."""
    if request.method == 'POST': # If the form has been submitted
        form = forms.ImportForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            import_file = request.FILES['import_file']
            return render_to_response('pharmaship/import.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'rank': request.user.profile.get_rank(),
                        'title':_("Allowance Settings"),
                        'data': import_archive(import_file),
                        },
                        context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(reverse('inventory_settings'))
    else:
        return HttpResponseRedirect(reverse('inventory_settings'))

@permission_required('inventory.location.can_add')
def create_location(request):
    """Creates a new Location for items in Inventory application."""
    if request.method == 'POST':
        form = forms.LocationCreateForm(request.POST)
        if form.is_valid():
            primary = form.cleaned_data['primary']
            secondary = form.cleaned_data['secondary']
            # Creation of the instance
            models.Location(primary=primary, secondary=secondary).save()
            return HttpResponseRedirect(reverse('inventory_settings'))
        else:
            return HttpResponseRedirect(reverse('inventory_settings'))
    else:
        return HttpResponseRedirect(reverse('inventory_settings'))

@permission_required('inventory.location.can_delete')
def delete_location(request):
    """Deletes selected Location objects for items in Inventory application."""
    if request.method == 'POST':
        form = forms.LocationDeleteForm(request.POST)
        if form.is_valid():
            obj = form.cleaned_data['to_delete']

            # Changing values for objects with location in obj
            default = models.Location.objects.get(pk=1)
            models.Medicine.objects.filter(location__in=obj).update(location = default)
            models.Article.objects.filter(location__in=obj).update(location = default)
            obj.delete()
            return HttpResponseRedirect(reverse('inventory_settings'))
        else:
            return HttpResponseRedirect(reverse('inventory_settings'))
    else:
        return HttpResponseRedirect(reverse('inventory_settings'))
