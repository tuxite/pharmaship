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

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.db import models
import datetime

# Constants
## Transaction type values
TYPE_CHOICES = (
        (1, 'In'),
        (2, 'Utilisé'),
        (4, 'Périmé'),
        (8, 'Physical Count'),
        (9, 'Other'),
    )

## Drug "dangerosity" list values
DRUG_LIST_CHOICES = (
        (0, 'None'),
        (1, 'Liste I'),
        (2, 'Liste II'),
        (9, 'Stupéfiants'),
    )

## Dosage form possible values
DRUG_FORM_CHOICES = (
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

## Route of administration possible values
DRUG_ROA_CHOICES = (
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

# Models
class Dotation(models.Model):
    """Model for articles and drugs dotations."""
    name = models.CharField(max_length=100) # Example: Dotation A
    additional = models.BooleanField(default=False) # For use with complements. True will add quantity, false will be treated as an absolute quantity.

    def __unicode__(self):
        return self.name

class DrugGroup(models.Model):
    """Model for groups attached to an INN (BaseDrug)."""
    name = models.CharField(max_length=100) # Example: Cardiology
    order = models.IntegerField() # Example: 1

    def __unicode__(self):
        return u"{0}. {1}".format(self.order, self.name)

    class Meta:
        ordering = ("order", "name",)

class Tag(models.Model):
    """Model for tags attached to an INN."""
    name = models.CharField(max_length=100) # Example: Common Use
    comment = models.TextField(blank=True, null=True) # Description of the tag, if any

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ("name",)        

class Drug(models.Model):
    """Drug model, "child" of BaseDrug."""
    exp_date = models.DateField()
    name = models.CharField(max_length=100) # Brand Name. Example: Doliprane for INN Paracétamol
    # Fields for non-conformity compatibility
    nc_inn = models.CharField(max_length=100, blank=True, null=True)
    nc_composition = models.CharField(max_length=100, blank=True, null=True)
    # Field to simplify SQL requests when qty=0
    used = models.BooleanField(default=False)

    def __unicode__(self):
        return u"{0} (exp: {1})".format(self.name, self.exp_date)

    def get_quantity(self):
        """Computes the quantity according to the transactions attached to this drug."""
        return DrugQtyTransaction.objects.filter(drug=self).aggregate(models.Sum('value'))['value__sum']


class BaseDrug(models.Model):
    """Base drug model for all drugs.
    inn = International Nonproprietary Name (DC in French)"""
    inn = models.CharField(max_length=100) # Example: Paracétamol
    roa = models.PositiveIntegerField(choices=DRUG_ROA_CHOICES) # Example: dermal -- ROA: Route of Administration
    dosage_form = models.IntegerField(choices=DRUG_FORM_CHOICES) # Example: "pill"
    composition = models.CharField(max_length=100) # Example: 1000 mg
    drug_list = models.PositiveIntegerField(choices=DRUG_LIST_CHOICES) # Example: List I
    location = models.CharField(max_length=100, blank=True, null=True) # Example: Pharmacy
    remark = models.TextField(blank=True, null=True)
    group = models.ForeignKey(DrugGroup)
    tag = models.ManyToManyField(Tag, blank=True)
    drug_items = models.ManyToManyField(Drug, through='DrugTransaction')
    dotations = models.ManyToManyField(Dotation, through='DrugReqQty')

    # Operations
    def __unicode__(self):
        return u"{0} ({2} - {1})".format(self.inn, self.composition, self.get_dosage_form_display())

    def get_quantity(self):
        """Computes the total quantity of non-expired & non-equivalent drugs attached to this INN."""
        total = 0
        for item in self.drug_items.filter(used=False):
            if item.exp_date > datetime.date.today() and not item.nc_inn and not item.nc_composition: ## Kind of validation
                total += item.get_quantity()
        return total

    def get_not_null(self):
        """Returns all Drug items with .used=False (qty>0).
        Used in templates."""
        return self.drug_items.filter(used=False)

    def get_required_quantity(self):
        """Computes the total required quantity of the INN."""
        ## TODO Dynamic filter by dotation
        maximum = self.dotations.filter(additional=False).aggregate(max=models.Max('drugreqqty__required_quantity'))['max']
        if not maximum:
            maximum = 0
        additional = self.dotations.filter(additional=True).aggregate(sum=models.Sum('drugreqqty__required_quantity'))['sum']
        if not additional:
            additional = 0
        return maximum + additional

    class Meta:
        ordering = ('inn', )


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


class DrugReqQty(models.Model):
    """Model for required quantity of a drug"""
    dotation = models.ForeignKey('Dotation')
    inn = models.ForeignKey('BaseDrug')
    required_quantity = models.IntegerField()

