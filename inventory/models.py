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
# Description: Models for Inventory application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

import ast

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


class GroupManager(models.Manager):
    """Manager for class MedicineGroup and MaterialGroup.
    For deserialization purpose only.
    """
    def get_by_natural_key(self, name):
        return self.get(name = name, )

        
class MoleculeGroup(models.Model):
    """Model for groups attached to an INN (Molecule)."""
    objects = GroupManager() # For deserialization

    name = models.CharField(max_length=100) # Example: Cardiology
    order = models.IntegerField() # Example: 1

    def __unicode__(self):
        return u"{0}. {1}".format(self.order, self.name)

    def natural_key(self):
            return (self.name,)

    class Meta:
        ordering = ("order", "name",)
        unique_together = ('name', )


class EquipmentGroup(models.Model):
    """Model for groups attached to a ReferenceMaterial."""
    objects = GroupManager() # For deserialization

    name = models.CharField(max_length=100) # Example: Reanimation
    order = models.IntegerField() # Example: 1

    def __unicode__(self):
        return u"{0}. {1}".format(self.order, self.name)

    def natural_key(self):
            return (self.name,)

    class Meta:
        ordering = ("order", "name",)
        unique_together = ('name', )


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
    primary = models.CharField(_("Primary"), max_length=100) # Example: Pharmacie
    secondary = models.CharField(_("Secondary"), max_length=100,blank=True, null=True) # Example: Tiroir 2

    def __unicode__(self):
        if self.secondary:
            return u"{0} > {1}".format(self.primary, self.secondary)
        else:
            return self.primary


    class Meta:
        ordering = ("primary", "secondary")


class QtyTransaction(models.Model):
    """
    Stores a quantity transaction related to :model:`inventory.Article` or :model:`inventory.Medicine`.

    There are 5 types of transactions :
    * 1 IN: a material is added,
    * 2 USED: the material is used for a treatment,
    * 4 PERISHED: the material has expired,
    * 8 PHYSICAL_COUNT: the stock is refreshed after a human count,
    * 9 OTHER: other reason.
    """

    transaction_type = models.PositiveIntegerField(_("Type"), choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    remark = models.TextField(blank=True, null=True)
    value = models.IntegerField(_("Value"), )

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return u"{0} ({1}: {2})".format(self.content_object, self.get_transaction_type_display(), self.value)


class Remark(models.Model):
    """Model for remarks attached to an INN."""
    text = models.TextField(_("Text"), blank=True, null=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


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
    group = models.ForeignKey(MoleculeGroup)
    tag = models.ManyToManyField(Tag, blank=True)
    allowances = models.ManyToManyField(Allowance, through='MoleculeReqQty')
    remark = generic.GenericRelation(Remark)

    def __unicode__(self):
        return u"{0} ({2} - {1})".format(self.name, self.composition, self.get_dosage_form_display())

    def natural_key(self):
            return (self.name, self.roa, self.dosage_form, self.composition)

    def order_info(self):
        """Outputs a string for Purchase application."""
        s = u"{0} {1} - {2} {3}".format(_("Dosage Form:"), self.get_dosage_form_display(), _("Composition:"), self.composition)
        return s

    class Meta:
        ordering = ('name', )
        unique_together = (('name', 'roa', 'dosage_form', 'composition'),)


class Medicine(models.Model):
    """Medicine model, "child" of Molecule."""
    name = models.CharField(_("Name"), max_length=100) # Brand Name. Example: Doliprane for INN Paracétamol
    exp_date = models.DateField(_("Expiration Date"))
    # Link to location
    location = models.ForeignKey(Location)
    # Fields for non-conformity compatibility
    nc_molecule = models.CharField(_("Non-conform Molecule"), max_length=100, blank=True, null=True)
    nc_composition = models.CharField(_("Non-conform Composition"), max_length=100, blank=True, null=True)
    # Field to simplify SQL requests when qty=0
    used = models.BooleanField(default=False)
    # Common
    transactions = generic.GenericRelation(QtyTransaction)
    parent = models.ForeignKey(Molecule)

    def __unicode__(self):
        return u"{0} (exp: {1})".format(self.name, self.exp_date)

    def get_quantity(self):
        """Computes the quantity according to the transactions attached to this medicine."""
        return self.transactions.aggregate(sum=models.Sum('value'))['sum']


    class Meta:
        ordering = ("exp_date", )


class MoleculeReqQty(models.Model):
    """Model for required quantity of a medicine"""
    allowance = models.ForeignKey('Allowance')
    base = models.ForeignKey('Molecule')
    required_quantity = models.IntegerField()


class EquipmentManager(models.Manager):
    """
    Manager for class Equipment.
    For deserialization purpose only.
    """
    def get_by_natural_key(self, name, packaging, consumable, perishable, group):
        return self.get(
            name = name,
            packaging = packaging,
            consumable = ast.literal_eval(consumable),
            perishable = ast.literal_eval(perishable),
            group = EquipmentGroup.objects.get_by_natural_key(ast.literal_eval(group)[0]),
            )

class Equipment(models.Model):
    """Model for medical equipment."""
    objects = EquipmentManager() # For deserialization

    name = models.CharField(max_length=100) # Example: Nébulisateur
    packaging = models.CharField(max_length=100) # Example: 1000 mg
    group = models.ForeignKey(EquipmentGroup)
    tag = models.ManyToManyField(Tag, blank=True)
    consumable = models.BooleanField(default=False)
    perishable = models.BooleanField(default=False)
    allowances = models.ManyToManyField(Allowance, through='EquipmentReqQty')
    remark = generic.GenericRelation(Remark)
    picture = models.ImageField(upload_to="pictures", blank=True, null=True)

    def __unicode__(self):
        return self.name

    def natural_key(self):
            return (self.name, self.packaging, self.consumable, self.perishable, self.group.natural_key())

    def order_info(self):
        """Outputs a string for Purchase application."""
        s = u"{0} {1}".format(_("Packaging:"), self.packaging)
        return s
        
    class Meta:
        ordering = ('name', )
        unique_together = (('name', 'packaging', 'consumable', 'perishable', 'group'),)


class Article(models.Model):
    """Article model, "child" of Equipment."""
    name = models.CharField(_("Name"), max_length=100) # Brand Name. Example: Coalgan
    exp_date = models.DateField(_("Expiration Date"), blank=True, null=True)
    # Link to location
    location = models.ForeignKey(Location)
    # Fields for non-conformity compatibility
    nc_packaging = models.CharField(_("Non-conform Packaging"), max_length=100, blank=True, null=True)
    # Field to simplify SQL requests when qty=0
    used = models.BooleanField(default=False)
    # Common
    transactions = generic.GenericRelation(QtyTransaction)
    parent = models.ForeignKey(Equipment)

    def __unicode__(self):
        return u"{0} (exp: {1})".format(self.name, self.exp_date)

    def get_quantity(self):
        """Computes the quantity according to the transactions attached to this medicine."""
        return self.transactions.aggregate(sum=models.Sum('value'))['sum']


    class Meta:
        ordering = ("exp_date", )


class EquipmentReqQty(models.Model):
    """Model for required quantity of a medical equipment"""
    allowance = models.ForeignKey('Allowance')
    base = models.ForeignKey('Equipment')
    required_quantity = models.IntegerField()


class Settings(models.Model):
    """Application settings."""
    allowance = models.ManyToManyField(Allowance, verbose_name=_('Allowance'))
    expire_date_warning_delay = models.PositiveIntegerField(_("Warning Delay for Expiration Dates"))
    

# Orderable objects
ORDERABLE = [Equipment, Molecule]
