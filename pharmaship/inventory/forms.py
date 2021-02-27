# -*- coding: utf-8; -*-
"""Inventory application forms."""
from django import forms
from django.utils.translation import gettext as _

import pharmaship.inventory.models


class AddMedicineForm(forms.ModelForm):
    """Form used for adding a medicine."""

    name = forms.CharField(max_length=100)
    quantity = forms.IntegerField(min_value=1)
    exp_date = forms.DateField()

    location_id = forms.IntegerField(min_value=1)
    parent_id = forms.IntegerField(min_value=1)

    nc_composition = forms.CharField(max_length=100, required=False)
    nc_molecule = forms.CharField(max_length=100, required=False)

    remark = forms.CharField(max_length=256, required=False)

    packing_combo_id = forms.IntegerField(min_value=0)
    packing_content = forms.IntegerField(min_value=1)

    class Meta:  # noqa: D106
        model = pharmaship.inventory.models.Medicine
        exclude = ['used', 'location', 'parent', 'packing_name']


class ModifyMedicineForm(forms.ModelForm):
    """Form used for modifying a `Medicine`."""

    name = forms.CharField(max_length=100)
    quantity = forms.IntegerField(min_value=1)
    exp_date = forms.DateField()

    location_id = forms.IntegerField(min_value=1)

    nc_composition = forms.CharField(max_length=100, required=False)
    nc_molecule = forms.CharField(max_length=100, required=False)

    remark = forms.CharField(max_length=256, required=False)

    packing_combo_id = forms.IntegerField(min_value=0)
    packing_content = forms.IntegerField(min_value=1)

    class Meta:  # noqa: D106
        model = pharmaship.inventory.models.Medicine
        exclude = ['used', 'location', 'parent', 'packing_name']


class AddArticleForm(forms.ModelForm):
    """Form used for adding an `Article`."""

    name = forms.CharField(max_length=100)
    quantity = forms.IntegerField(min_value=1)
    exp_date = forms.DateField(required=False)

    location_id = forms.IntegerField(min_value=1)
    parent_id = forms.IntegerField(min_value=1)
    perishable = forms.BooleanField(required=False)

    nc_packaging = forms.CharField(max_length=100, required=False)

    remark = forms.CharField(max_length=256, required=False)

    packing_combo_id = forms.IntegerField(min_value=0)
    packing_content = forms.IntegerField(min_value=1)

    def clean(self):
        """Check that a date is correct if needed by the model.

        This method completes the standard validation method and adds a
        conditional check of the date through the `perishable` attribute.
        If `True`, an `exp_date` must be present and correct.
        """
        cleaned_data = super().clean()

        if not cleaned_data.get("perishable"):
            return cleaned_data

        if not cleaned_data.get("exp_date"):
            self.add_error(
                "exp_date",
                forms.ValidationError(
                    _('Expiry date must be provided.'),
                    code='required')
                    )

    class Meta:  # noqa: D106
        model = pharmaship.inventory.models.Article
        exclude = ['used', 'location', 'parent', 'packing_name']


class ModifyArticleForm(forms.ModelForm):
    """Form used for modifying an `Article`."""

    name = forms.CharField(max_length=100)
    quantity = forms.IntegerField(min_value=1)
    exp_date = forms.DateField(required=False)

    location_id = forms.IntegerField(min_value=1)

    nc_packaging = forms.CharField(max_length=100, required=False)

    remark = forms.CharField(max_length=256, required=False)

    packing_combo_id = forms.IntegerField(min_value=0)
    packing_content = forms.IntegerField(min_value=1)

    class Meta:  # noqa: D106
        model = pharmaship.inventory.models.Article
        exclude = ['used', 'location', 'parent', 'packing_name']


class LocationForm(forms.ModelForm):
    """Form used to add a `Location`."""

    parent_id = forms.IntegerField(required=False)
    name = forms.CharField(max_length=100)

    class Meta:  # noqa: D106
        model = pharmaship.inventory.models.Location
        exclude = ['parent', ]


class InventorySettingsForm(forms.Form):
    """Form used to modify the inventory `Setting`."""

    expire_date_warning_delay = forms.IntegerField(min_value=15)
    rescue_bag = forms.IntegerField(min_value=1)
    first_aid_kit = forms.IntegerField(min_value=1)
    has_laboratory = forms.BooleanField(required=False)
    has_telemedical = forms.BooleanField(required=False)

    # class Meta:  # noqa: D106
    #     model = pharmaship.inventory.models.Settings
    #     exclude = ['allowance', ]


class FirstAidKitForm(forms.Form):
    """Form used to modify a `FirstAidKit`."""

    name = forms.CharField(max_length=100)
    location_id = forms.IntegerField(min_value=1)

    class Meta:  # noqa: D106
        model = pharmaship.inventory.models.FirstAidKit
        exclude = ['location', ]


class AddSubitemForm(forms.Form):
    """Form used to add a `FirstAidKitItem`."""

    item_id = forms.IntegerField(min_value=1)
    quantity = forms.IntegerField(min_value=1)
    remark = forms.CharField(max_length=256, required=False)


class AddNewSubitemForm(forms.Form):
    """Form used to add a new `FirstAidKitItem`."""

    name = forms.CharField(max_length=100)
    quantity = forms.IntegerField(min_value=1)
    exp_date = forms.DateField(required=False)
    remark = forms.CharField(max_length=256, required=False)
    nc = forms.CharField(max_length=256, required=False)

    # For exp_date required field validation
    perishable = forms.BooleanField(required=False)

    def clean(self):
        """Check that a date is correct if needed by the model.

        This method completes the standard validation method and adds a
        conditional check of the date through the `perishable` attribute.
        If `True`, an `exp_date` must be present and correct.
        """
        cleaned_data = super().clean()

        if not cleaned_data.get("perishable"):
            return cleaned_data

        if not cleaned_data.get("exp_date"):
            self.add_error(
                "exp_date",
                forms.ValidationError(
                    _('Expiry date must be provided.'),
                    code='required')
                    )


class ModifySubitemForm(forms.Form):
    """Form used to modify a `FirstAidKitItem`."""

    quantity = forms.IntegerField(min_value=1)
    remark = forms.CharField(max_length=256, required=False)
    nc = forms.CharField(max_length=256, required=False)
    exp_date = forms.CharField(max_length=256, required=False)
    # For exp_date required field validation
    perishable = forms.BooleanField(required=False)

    def clean(self):
        """Check that a date is correct if needed by the model.

        This method completes the standard validation method and adds a
        conditional check of the date through the `perishable` attribute.
        If `True`, an `exp_date` must be present and correct.
        """
        cleaned_data = super().clean()

        if not cleaned_data.get("perishable"):
            return cleaned_data

        if not cleaned_data.get("exp_date"):
            self.add_error(
                "exp_date",
                forms.ValidationError(
                    _('Expiry date must be provided.'),
                    code='required')
                    )


class RescueBagForm(forms.ModelForm):
    """Form used to modify a `RescueBag`."""

    name = forms.CharField(max_length=100)
    location_id = forms.IntegerField(min_value=1)

    class Meta:  # noqa: D106
        model = pharmaship.inventory.models.RescueBag
        exclude = ['location', ]
