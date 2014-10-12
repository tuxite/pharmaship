# -*- coding: utf-8; -*-
from django.utils.translation import ugettext_lazy as _
from django import forms

from core.forms import DateInput
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
    reason = forms.ChoiceField(choices=DELETE_REASON, label=_("Reason"))


class ChangeMedicineForm(forms.ModelForm):
    """Form used for changing the details and the quantity of an object in the list."""
    quantity = forms.IntegerField(label=_("Quantity in stock"))
    exp_date = forms.DateField(label=_("Expiration Date"), widget=DateInput())

    class Meta:
        model = models.Medicine
        exclude = ['nc_composition', 'nc_molecule', 'used', 'parent']


class QtyChangeForm(forms.Form):
    """Form used for changing the quantity of an object in the list."""
    quantity = forms.IntegerField(label=_("Quantity"))


class AddMedicineForm(forms.ModelForm):
    """Form used for adding a medicine to an INN in the list."""
    quantity = forms.IntegerField(label=_("Quantity"))
    exp_date = forms.DateField(label=_("Expiration Date"), widget=DateInput())
    nc_composition = forms.CharField(label=_("Composition"))


    class Meta:
        model = models.Medicine
        exclude = ['used', 'nc_molecule', 'parent']


class AddEquivalentForm(forms.ModelForm):
    """Form used for adding an equivalent medicine to an INN in the list."""
    quantity = forms.IntegerField(label=_("Quantity"))
    exp_date = forms.DateField(label=_("Expiration Date"), widget=DateInput())
    nc_composition = forms.CharField(label=_("Composition"))
    nc_molecule = forms.CharField(label=_("Molecule"))


    class Meta:
        model = models.Medicine
        exclude = ['used', 'parent']


class MoleculeForm(forms.ModelForm):
    """Form used in Admin view."""
    tag = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=models.Tag.objects.all(), required=False)


    class Meta:
        model = models.Molecule
        exclude = []


class RemarkForm(forms.Form):
    """Form to change the remark of an object in a view."""
    text = forms.CharField(widget=forms.Textarea)


class AddArticleForm(forms.ModelForm):
    """Form used for adding a material to a reference material in the list."""
    quantity = forms.IntegerField(label=_("Quantity"))
    exp_date = forms.DateField(label=_("Expiration Date"), widget=DateInput())
    nc_packaging = forms.CharField(label=_("Packaging"))


    class Meta:
        model = models.Article
        exclude = ['used', 'parent']


class ChangeArticleForm(forms.ModelForm):
    """Form used for changing the details and the quantity of an object in the list."""
    quantity = forms.IntegerField(label=_('Quantity in stock'))
    exp_date = forms.DateField(label=_("Expiration Date"), widget=DateInput())


    class Meta:
        model = models.Article
        exclude = ['nc_packaging', 'used', 'parent']


class SettingsForm(forms.ModelForm):
    """Form to modify Pharmaship dedicated settings."""
    class Meta:
        model = models.Settings
        exclude = ['allowance',]


class LocationCreateForm(forms.ModelForm):
    """Form for creating a new Location."""
    class Meta:
        model = models.Location
        exclude = []
