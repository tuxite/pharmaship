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

__author__ = "Django Project, Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django import forms

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
    """ Form used for deleting an objet in the list."""
    reason = forms.ChoiceField(choices=DELETE_REASON)

class QtyChangeForm(forms.Form):
    """ Form used for changing the quantity of an objet in the list."""
    quantity = forms.IntegerField()

class AddForm(forms.Form):
    """ Form used for adding a drug to an INN in the list."""
    name = forms.CharField()
    nc_dose = forms.CharField()
    quantity = forms.IntegerField()
    exp_date = forms.DateField()

class AddEquivalentForm(forms.Form):
    """ Form used for adding an equivalent drug to an INN in the list."""
    name = forms.CharField()
    nc_inn = forms.CharField()    
    nc_dose = forms.CharField()
    quantity = forms.IntegerField()
    exp_date = forms.DateField()
    
