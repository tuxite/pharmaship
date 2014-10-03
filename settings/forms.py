# -*- coding: utf-8; -*-
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

class ImportKeyForm(forms.Form):
    """Form used to import PGP key into Onboard Assistant."""
    file_obj = forms.FileField(label=_("Key"))