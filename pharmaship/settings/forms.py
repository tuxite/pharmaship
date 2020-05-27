# -*- coding: utf-8 -*-
"""Forms for Settings module."""
from django import forms
from django.core.validators import MaxValueValidator


class VesselSettingsForm(forms.Form):
    """Form used for modifying vessel settings."""

    name = forms.CharField(max_length=50)
    imo = forms.IntegerField(validators=[
        MaxValueValidator(9999999)
    ])
    call_sign = forms.CharField(max_length=30)
    sat_phone = forms.CharField(max_length=20)
    gsm_phone = forms.CharField(max_length=20)
    flag = forms.CharField(max_length=30)
    port_of_registry = forms.CharField(max_length=100)
    shipowner = forms.CharField(max_length=100)
    mmsi = forms.IntegerField(validators=[
        MaxValueValidator(999999999)
    ])
    email = forms.EmailField(max_length=254)

    address = forms.CharField()
