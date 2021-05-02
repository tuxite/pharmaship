# -*- coding: utf-8; -*-
"""Translation registering for Inventory models."""
from modeltranslation.translator import register, TranslationOptions
from pharmaship.inventory import models


@register(models.Equipment)
class EquipmentTranslationOptions(TranslationOptions):
    fields = ('name', 'packaging', 'remark')


@register(models.Molecule)
class MoleculeTranslationOptions(TranslationOptions):
    fields = ('name', 'composition', 'remark')


@register(models.EquipmentGroup)
class EquipmentGroupTranslationOptions(TranslationOptions):
    fields = ('name', )


@register(models.MoleculeGroup)
class MoleculeGroupTranslationOptions(TranslationOptions):
    fields = ('name', )
