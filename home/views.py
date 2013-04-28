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
# Filename:    home/views.py
# Description: Views for Home application. Used for contact view.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render_to_response('index.html', {'user': (request.user.last_name + " " +request.user.first_name), 'title':"Accueil", 'rank': request.user.profile.get_rank()})

def contact(request):
    title = "Contacter le CCMM"
    if request.user.is_authenticated():
        variables = {'title': title, 'user':(request.user.last_name + " " +request.user.first_name), 'rank': request.user.profile.get_rank()}
    else:
        variables = {'title':title}
    return render_to_response('contact.html', variables)
