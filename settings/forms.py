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
# Filename:    settings/forms.py
# Description: Forms classes for Settings application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.2"

from django.utils.translation import ugettext as _
from django import forms

import models
    
class UserForm(forms.ModelForm):
    """Form used to customize User parameters."""
    class Meta:
        model = models.User
        fields = ['last_name', 'first_name', 'function']

class VesselForm(forms.ModelForm):
    """Form used to input Vessel data."""
    class Meta:
        model = models.Vessel
        exclude = []
        

class ImportForm(forms.Form):
    """Form used to import data into Onboard Assistant."""
    file_obj = forms.FileField(label=_("File"))
