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

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import ModelForm
from django.template import RequestContext
from django.http import HttpResponseRedirect

from models import Vessel, Application
from forms import VesselForm, ApplicationForm

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
    return render_to_response('settings.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'rank': request.user.profile.get_rank(),
                        'title':"Paramètres du compte",
                        'vesselform':VesselForm(instance=Vessel.objects.latest('id')).as_table(),
                        'userform':UserForm(instance=User.objects.get(id=request.user.id)).as_table(),
                        'userprofileform':UserProfileForm(instance=UserProfile.objects.get(id=request.user.id)).as_table(),
                        'applicationform': ApplicationForm(instance=Application.objects.latest('id')).as_table(),
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

@permission_required('users.user_profile.can_change')
def user(request):
    """Validation of the User and UserProfile forms."""
    if request.method == 'POST':
        validation(request, UserForm, User.objects.get(id=request.user.id))
        validation(request, UserProfileForm, UserProfile.objects.get(id=request.user.id))

    return HttpResponseRedirect('/settings') # Redirect after POST
    
@permission_required('settings.vessel.can_change')
def vessel(request):
    """Validation of the Vessel form."""
    if request.method == 'POST':
        validation(request, VesselForm, Vessel.objects.latest('id'))

    return HttpResponseRedirect('/settings') # Redirect after POST    

@permission_required('settings.application.can_change')
def application(request):
    """Validation of the Application form."""
    if request.method == 'POST':
        validation(request, ApplicationForm, Application.objects.latest('id'))

    return HttpResponseRedirect('/settings') # Redirect after POST    
