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
from django.forms import ModelForm
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

import models, forms

from django.contrib.auth.models import User

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
            app_data['active'] = True
        # Looking if the applications has settings that can be imported
        elif globals().get("{0}.settings.urls".format(application), True):
            print "application"
            app_data['name'] = _(application.capitalize())
            app_data['url'] = "{0}_settings".format(application)
        else:
            continue
        links.append(app_data)
            
    return render_to_response('settings.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'rank': request.user.profile.get_rank(),
                        'title': _("Settings"),
                        'links': links,
                        'vesselform': forms.VesselForm(instance = models.Vessel.objects.latest('id')).as_table(),
                        'userform': forms.UserForm(instance = User.objects.get(id = request.user.id)).as_table(),
                        'userprofileform': forms.UserProfileForm(instance = models.UserProfile.objects.get(id = request.user.id)).as_table(),
                        },
                        context_instance=RequestContext(request))

@permission_required('settings')
def validation(request, form, instance=None):
    """Validates the form in args."""
    f = form(request.POST, instance=instance)
    if f.is_valid(): # All validation rules pass
        f.save()
    else:
        # TODO: Error message
        return False

@permission_required('settings.user_profile.can_change')
def user(request):
    """Validation of the User and UserProfile forms."""
    if request.method == 'POST':
        validation(request, forms.UserForm, User.objects.get(id=request.user.id))
        validation(request, forms.UserProfileForm, models.UserProfile.objects.get(id=request.user.id))

    return HttpResponseRedirect('/settings') # Redirect after POST

@permission_required('settings.vessel.can_change')
def vessel(request):
    """Validation of the Vessel form."""
    if request.method == 'POST':
        validation(request, forms.VesselForm, models.Vessel.objects.latest('id'))

    return HttpResponseRedirect('/settings') # Redirect after POST

