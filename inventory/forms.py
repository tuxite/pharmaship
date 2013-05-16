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
# Filename:    inventory/forms.py
# Description: Forms classes for Inventory application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django import forms
import models

DELETE_REASON = (
        (4, 'Péremption'),
        (9, 'Autre'),
    )

CHANGE_REASON = (
        (2, 'Utilisé'),
        (8, 'Physical Count'),
        (9, 'Other'),
    )

class DeleteForm(forms.Form):
    """Form used for deleting an objet in the list."""
    reason = forms.ChoiceField(choices=DELETE_REASON)


class InfoChangeForm(forms.ModelForm):
    """Form used for changing the details and the quantity of an object in the list."""
    quantity = forms.IntegerField()

    class Meta:
        model = models.Drug
        exclude = ['nc_composition', 'nc_inn', 'used']

class QtyChangeForm(forms.Form):
    """Form used for changing the quantity of an object in the list."""
    quantity = forms.IntegerField()

class AddForm(forms.Form):
    """Form used for adding a drug to an INN in the list."""
    name = forms.CharField()
    nc_composition = forms.CharField()
    quantity = forms.IntegerField()
    exp_date = forms.DateField()


class AddEquivalentForm(forms.Form):
    """Form used for adding an equivalent drug to an INN in the list."""
    name = forms.CharField()
    nc_inn = forms.CharField()
    nc_composition = forms.CharField()
    quantity = forms.IntegerField()
    exp_date = forms.DateField()


class BaseDrugForm(forms.ModelForm):
    """Form used in Admin view."""
    tag = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=models.Tag.objects.all(), required=False)

    class Meta:
        model = models.BaseDrug

class BaseDrugLocRemForm(forms.ModelForm):
    """Form to change the location and the remark of a BaseDrug in a view."""
    class Meta:
        model = models.BaseDrug
        fields = ['location', 'remark']
