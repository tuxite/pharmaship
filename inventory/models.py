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

import settings.models

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

## Medicine "dangerosity" list values
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
class Allowance(models.Model):
    """Model for articles and medicines allowances."""
    name = models.CharField(max_length=100) # Example: Dotation A
    additional = models.BooleanField(default=False) # For use with complements. True will add quantity, false will be treated as an absolute quantity.

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('name', )

class MedicineGroupManager(models.Manager):
    """
    Manager for class MedicineGroup.
    For deserialization purpose only.
    """
    def get_by_natural_key(self, name):
        return self.get(name=name)
        
class MedicineGroup(models.Model):
    """Model for groups attached to an INN (Molecule)."""
    objects = MedicineGroupManager() # For deserialization
    
    name = models.CharField(max_length=100) # Example: Cardiology
    order = models.IntegerField() # Example: 1

    def __unicode__(self):
        return u"{0}. {1}".format(self.order, self.name)

    class Meta:
        ordering = ("order", "name",)
        unique_together = ('name', )

    def natural_key(self):
            return (self.name,)
            
class TagManager(models.Manager):
    """
    Manager for class Tag.
    For deserialization purpose only.
    """
    def get_by_natural_key(self, name):
        return self.get(name=name)
        
class Tag(models.Model):
    """Model for tags attached to an INN."""
    objects =TagManager() # For deserialization
    
    name = models.CharField(max_length=100) # Example: Common Use
    comment = models.TextField(blank=True, null=True) # Description of the tag, if any

    def __unicode__(self):
        return self.name

    def natural_key(self):
            return (self.name,)
            
    class Meta:
        ordering = ("name",)
        unique_together = ('name',)
        

            
class Location(models.Model):
    """Model for locations attached to a Medicine."""
    primary = models.CharField(max_length=100) # Example: Pharmacie
    secondary = models.CharField(max_length=100,blank=True, null=True) # Example: Tiroir 2

    def __unicode__(self):
        if self.secondary:
            return u"{0} > {1}".format(self.primary, self.secondary)
        else:
            return self.primary


class Medicine(models.Model):
    """Medicine model, "child" of Molecule."""
    name = models.CharField(max_length=100) # Brand Name. Example: Doliprane for INN Paracétamol
    exp_date = models.DateField()
    # Link to location
    location = models.ForeignKey(Location)
    # Fields for non-conformity compatibility
    nc_inn = models.CharField(max_length=100, blank=True, null=True)
    nc_composition = models.CharField(max_length=100, blank=True, null=True)
    # Field to simplify SQL requests when qty=0
    used = models.BooleanField(default=False)

    def __unicode__(self):
        return u"{0} (exp: {1})".format(self.name, self.exp_date)

    def get_quantity(self):
        """Computes the quantity according to the transactions attached to this medicine."""
        return self.medicineqtytransaction_set.aggregate(sum=models.Sum('value'))['sum']

class MoleculeManager(models.Manager):
    """
    Manager for class Molecule.
    For deserialization purpose only.
    """
    def get_by_natural_key(self, name, roa, dosage_form, composition):
        return self.get(name=name, roa=roa, dosage_form=dosage_form, composition=composition)
        
class Molecule(models.Model):
    """Base medicine model for all medicines.
    inn = International Nonproprietary Name (DC in French)"""
    objects = MoleculeManager() # For deserialization
    
    name = models.CharField(max_length=100) # Example: Paracétamol
    roa = models.PositiveIntegerField(choices=DRUG_ROA_CHOICES) # Example: dermal -- ROA: Route of Administration
    dosage_form = models.IntegerField(choices=DRUG_FORM_CHOICES) # Example: "pill"
    composition = models.CharField(max_length=100) # Example: 1000 mg
    medicine_list = models.PositiveIntegerField(choices=DRUG_LIST_CHOICES) # Example: List I
    group = models.ForeignKey(MedicineGroup)
    tag = models.ManyToManyField(Tag, blank=True)
    medicine_items = models.ManyToManyField(Medicine, through='MedicineTransaction')
    allowances = models.ManyToManyField(Allowance, through='MedicineReqQty')

    # Operations
    def __unicode__(self):
        return u"{0} ({2} - {1})".format(self.name, self.composition, self.get_dosage_form_display())

    def get_quantity(self):
        """Computes the total quantity of non-expired & non-equivalent medicines attached to this INN."""
        total = 0
        for item in self.medicine_items.filter(used=False):
            if item.exp_date > datetime.date.today() and not item.nc_inn and not item.nc_composition: ## Kind of validation
                total += item.get_quantity()
        return total

    def get_not_null(self):
        """Returns all Medicine items with .used=False (qty>0).
        Used in templates."""
        return self.medicine_items.filter(used=False)

    def get_required_quantity(self):
        """Computes the total required quantity of the INN."""
        # Workaround: Use the Settings.Vessel.allowance to get the list
        allowance_list = settings.models.Vessel.objects.latest('id').allowance.all();

        # For non-additional allowances, the required quantity is a minimum, so we keep the highest required quantity in the set.
        maximum = self.allowances.filter(additional=False, id__in=allowance_list).aggregate(max=models.Max('medicinereqqty__required_quantity'))['max']
        if not maximum:
            maximum = 0

        # Additional allowances, adds quantity to the inn. We keep the sum of the required quantities in the set.
        additional = self.allowances.filter(additional=True, id__in=allowance_list).aggregate(sum=models.Sum('medicinereqqty__required_quantity'))['sum']
        if not additional:
            additional = 0

        return maximum + additional

    def natural_key(self):
            return (self.name, self.roa, self.dosage_form, self.composition)
        
    class Meta:
        ordering = ('name', )
        unique_together = (('name', 'roa', 'dosage_form', 'composition'),)

class MedicineQtyTransaction(models.Model):
    """
    Stores a quantity transaction related to :model:`inventory.Medicine`.

    There are 5 types of transactions :
    * 1 IN: a medicine is added,
    * 2 USED: the medicine is used for a treatment,
    * 4 PERISHED: the medicine has expired,
    * 8 PHYSICAL_COUNT: the stock is refreshed after a human count,
    * 9 OTHER: other reason.
    """

    transaction_type = models.PositiveIntegerField(choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    remark = models.TextField(blank=True, null=True)
    value = models.IntegerField()
    medicine = models.ForeignKey('Medicine')

    def __unicode__(self):
        return u"{0} ({1}: {2})".format(self.medicine, self.get_transaction_type_display(), self.value)


class MedicineTransaction(models.Model):
    """Model which joins Medicine and Molecule models."""
    medicine = models.ForeignKey(Medicine)
    molecule = models.ForeignKey(Molecule)
    date = models.DateTimeField(auto_now_add=True)
    purchase_order = models.CharField(max_length=100, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)


class MedicineReqQty(models.Model):
    """Model for required quantity of a medicine"""
    allowance = models.ForeignKey('Allowance')
    inn = models.ForeignKey('Molecule')
    required_quantity = models.IntegerField()


class Remark(models.Model):
    """Model for remarks attached to an INN."""
    text = models.TextField(blank=True, null=True)
    molecule = models.OneToOneField('Molecule')
