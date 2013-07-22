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
__version__ = "0.1"

from django.forms.models import modelform_factory
from django import forms

import models
from inventory.models import Allowance

ApplicationForm = modelform_factory(models.Application)

class VesselForm(forms.ModelForm):
    allowance = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Allowance.objects.all().exclude(pk=0))

    class Meta:
        model = models.Vessel

class ExportForm(forms.Form):
    """Form for exporting a dotation (molecules, material and required quantities)."""
    allowance = forms.ModelChoiceField(queryset=Allowance.objects.all())

class ImportForm(forms.Form):
    """Form for importing a dotation (molecules, material and required quantities)."""
    import_file = forms.FileField()
