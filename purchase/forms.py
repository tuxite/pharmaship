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

from django.utils.translation import ugettext_lazy as _
from django import forms

from django.contrib.contenttypes.models import ContentType
from django.apps import apps

from core.forms import DateInput
import models

def get_model_choices():
    """Function to parse all installed applications to get the orderables models."""
    result = [] # Using model choices format.
    for application in apps.get_app_configs():
        try:
            obj = application.orderable()
        except AttributeError, e:
            #print "Error", application, e
            continue
            
        r = []
        for element in obj:
            # Parse with ContentType to get the model's id.
            element['id'] = ContentType.objects.get_for_model(element['object']).id
            # Add the information to a list to match the CharField choices expected format
            r.append([element['id'], element['name']])
        result.append([application.verbose_name, r])
    return result

class CreateRequisitionForm(forms.ModelForm):
    """Form for the creation of a new requisition."""
    auto_add = forms.BooleanField(label=_("Populate automatically"), required=False)
    requested_date = forms.DateField(label=_("Requested Date"), widget=DateInput())
    
    def __init__(self, *args, **kwargs):
       super(CreateRequisitionForm, self).__init__(*args, **kwargs)
       self.fields["item_type"] = forms.ChoiceField(choices=get_model_choices())
       
    class Meta:
        model = models.Requisition
        fields = ['name', 'requested_date', 'port_of_delivery', 'item_type']


class InstructionForm(forms.Form):
    """Form for editing instructions of a Requisition."""
    text = forms.CharField(required=False)


class RequisitionNameForm(forms.ModelForm):
    """Form for editing the name of a Requisition."""
    name = forms.CharField(label=_("Name"))

    class Meta:
        model = models.Requisition
        fields = ['name',]
    
    
class StatusForm(forms.ModelForm):
    """Form for editing instructions of a Requisition."""
    status = forms.ChoiceField(choices=models.STATUS_CHOICES)

    class Meta:
        model = models.Requisition
        fields = ['status',]

class NameSearchForm(forms.Form):
    """Form to sanitize the name search of an item."""
    name = forms.CharField()
    
class RequistionDeleteForm(forms.Form):
    """Form for deleting a requisition."""
    
class AddItemForm(forms.Form):
    """Form to add an item to a requisition."""
    object_id = forms.IntegerField()
    quantity = forms.IntegerField()

class UpdateItemQty(forms.Form):
    """Form to update thr item quantity."""
    item_id = forms.IntegerField()
    item_qty = forms.IntegerField()
