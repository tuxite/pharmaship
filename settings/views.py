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
from django.forms.models import modelformset_factory
from django.template import RequestContext
from django.http import HttpResponseRedirect


from models import Vessel
from django.contrib.auth.models import User
from users.models import UserProfile

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
    # Creating the formsets with adequate filters
    VesselFormSet = modelformset_factory(Vessel, max_num=1)
    UserFormSet = modelformset_factory(User, fields=('first_name', 'last_name'), max_num=1)
    UserProfileFormSet = modelformset_factory(UserProfile, fields=('function',), max_num=1)

    # Checking the input data
    if request.method == 'POST': # If the form has been submitted...
        # What is the form? User or Vessel
        if request.path.split("/")[-1] == "vessel":
            validation(request, [VesselFormSet,])
        else:
            validation(request, [UserFormSet, UserProfileFormSet])
        return HttpResponseRedirect('/settings') # Redirect after POST

    return render_to_response('settings.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'rank': request.user.profile.get_rank(),
                        'title':"Paramètres du compte",
                        'vesselformset':VesselFormSet(queryset=Vessel.objects.filter(id=6)).as_p(),
                        'userformset':UserFormSet(queryset=User.objects.filter(id=request.user.id)),
                        'userprofileformset':UserProfileFormSet(queryset=UserProfile.objects.filter(id=request.user.id)),
                        },
                        context_instance=RequestContext(request))

@permission_required('settings')
@login_required
def validation(request, forms):
    """Validates the forms in args."""
    for form in forms:
        f = form(request.POST) # A form bound to the POST data
        if f.is_valid(): # All validation rules pass
            f.save()
        else:
            return HttpResponseRedirect('/') # Redirect after POST   
