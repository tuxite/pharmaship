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
# Filename:    inventory/models.py
# Description: Models for Settings application.
# ======================================================================

__author__ = "Django Project, Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.db import models
from django import forms
import datetime

# Constants
TYPE_CHOICES = (
        (1, 'In'),
        (2, 'Utilisé'),
        (4, 'Périmé'),
        (8, 'Physical Count'),
        (9, 'Other'),
    )

DRUG_LIST_CHOICES = (
        (0, 'None'),
        (1, 'Liste I'),
        (2, 'Liste II'),
        (9, 'Stupéfiants'),
    )

DRUG_PACKAGING_CHOICES = (
        (1, 'Comprimé'),
        (2, 'Ampoule'),
        (3, 'Gélule'),
        (5, 'Lyophilisat oral'),
        (6, 'Sachet'),
        (7, 'Suppositoire'),
        (8, 'Capsule'),

        (10, 'Tube pommade'),
        (11, 'Tube crème'),
        (12, 'Gel buccal'),
        (13, 'Unidose gel'),

        (40, 'Seringue pré-remplie'),

        (50, 'Solution pour perfusion'),
        (51, 'Solution injectable'),
        (52, 'Solution acqueuse'),
        (53, 'Solution moussante'),
        (54, 'Solution alcoolisée'),
        (55, 'Solution auriculaire'),
        (56, 'Solution'),

        (90, 'Bouteille'),
        (91, 'Flacon'),
        (92, 'Dispositif'),
        (93, 'Pansement adhésif cutané'),
        (94, 'Unidose'),

        (100, 'Collyre unidose'),
        (101, 'Collyre flacon'),
        (102, 'Collutoire'),
        (103, 'Pommade ophtalmique'),

    )

DRUG_PATH_CHOICES = (
        (1, 'Orale'),
        
        (5, 'Parentérale'),
        (6, 'Sous-cutannée'),

        (10, 'Locale'),
        (11, 'Transdermique'),

        (20, 'Inhalation'),
        (21, 'Nébulisation'),

        (30, 'Buccale'),
        (31, 'Sublinguale'),
        (32, 'Bain de bouche'),

        (40, 'Rectale'),        
        (41, 'Vaginale'),

        (50, 'Oculaire'),        
        
    )
DOTATION_CHOICES = ( # TO BE DYNAMIC (for adding additional dotations)
        ('A', 'Dotation A'),
        ('B', 'Dotation B'),
        ('C', 'Dotation C'),
        ('P1', 'Complément P1'),
        ('P2', 'Complément P2'),
        ('P3', 'Complément P3'),
        ('P4', 'Complément P4'),
    )
# Objects
class DrugGroup(models.Model):
    """Group model for BaseDrug."""
    name = models.CharField(max_length=100) # Example: Cardiology

    def __unicode__(self):
        return self.name
    
class Drug(models.Model):
    """Drug model, "child" of BaseDrug."""
    exp_date = models.DateField()
    name = models.CharField(max_length=100) # Brand Name. Example: Doliprane for INN Paracétamol
    # Fields for non-conformity compatibility
    nc_inn = models.CharField(max_length=100, blank=True, null=True)
    nc_dose = models.CharField(max_length=100, blank=True, null=True)
    used = models.BooleanField(default=False)

    def __unicode__(self):
        return u"{0} (exp: {1})".format(self.name, self.exp_date)
        
    def get_quantity(self):
        """Computes the quantity according to the transactions attached to this drug."""
        return DrugQtyTransaction.objects.filter(drug=self).aggregate(models.Sum('value'))['value__sum']

       
class BaseDrug(models.Model):
    """Base drug model for all drugs.
    inn = International Nonproprietary Name (DC in French)"""
    # reference will be used as DCI name.
    inn = models.CharField(max_length=100) # Example: Paracétamol
    path = models.PositiveIntegerField(choices=DRUG_PATH_CHOICES) # Example: dermal
    packaging = models.IntegerField(choices=DRUG_PACKAGING_CHOICES) # Example: "pill"
    dose = models.DecimalField(max_digits=6, decimal_places=2) # Example: 1000 (mg)
    unit = models.CharField(max_length=100) # Example: "mg"
    required_quantity = models.PositiveIntegerField() # Example: 100
    drug_list = models.PositiveIntegerField(choices=DRUG_LIST_CHOICES) # Example: List I
    group = models.ManyToManyField(DrugGroup)
    dotation = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True) # Example: Pharmacy
    remark = models.TextField(blank=True, null=True)
    # Test relationship
    drug_items = models.ManyToManyField(Drug, through='DrugTransaction')
    
    # Operations
    def __unicode__(self):
        return u"{0} ({3} - {1} {2})".format(self.inn, self.dose, self.unit, self.get_packaging_display())

    def get_quantity(self):
        """Computes the total quantity of non-expired & non-equivalent drugs attached to this INN."""
        total = 0
        for item in self.drug_items.filter(used=False):
            if item.exp_date > datetime.date.today() and not item.nc_inn and not item.nc_dose: ## Kind of validation
                total += item.get_quantity()
        return total

    def is_valid(self):
        return True

    def get_groups(self):
        dgc = dict(DRUG_GROUP_CHOICES)
        result = ""
        for item in set(self.group):
            result += dgc[item]
        return result

    def get_not_null(self):
        result = []
        for item in Drug.objects.filter(basedrug=self):
            if item.get_quantity() > 0:
                result.append(item)
        return result
        
        
class BaseDrugForm(forms.ModelForm):
    group = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=DrugGroup.objects.all())
    dotation = forms.MultipleChoiceField(choices=DOTATION_CHOICES, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = BaseDrug
        
class DrugQtyTransaction(models.Model):
    """Model for all transactions (in, out, inventory count, ...)"""
    transaction_type = models.PositiveIntegerField(choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    remark = models.TextField(blank=True, null=True)
    value = models.IntegerField()
    drug = models.ForeignKey('Drug')

class DrugTransaction(models.Model):
    """Model which joins Drug and BaseDrug models."""
    drug = models.ForeignKey(Drug)
    basedrug = models.ForeignKey(BaseDrug)
    date = models.DateTimeField(auto_now_add=True)
    purchase_order = models.CharField(max_length=100, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    
#~ class BaseMaterial(BaseArticle):
    #~ """Base material model for all medical material."""
    #~ consumable = models.BooleanField() # Tag
    #~ exp_date = models.DateField()
