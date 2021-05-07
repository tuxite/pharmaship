# -*- coding: utf-8; -*-
"""Inventory application REST framework serializers.

Mainly used for exporting Allowance.
"""
from rest_framework import serializers
from generic_relations.relations import GenericRelatedField

from django.contrib.contenttypes.models import ContentType

from pharmaship.inventory import models


class MyGenericRelatedField(GenericRelatedField):
    """Generic related field used in First Aid Kits required quantity items."""


class ContentTypeSerializer(serializers.ModelSerializer):
    """Django ContentType serializer.

    Mainly used in Recue Bag and First Aid Kit required quantity serializers.
    """

    class Meta:  # noqa: D106
        model = ContentType
        fields = ["app_label", "name"]


class EquipmentSerializer(serializers.ModelSerializer):
    """Equipment serializer.

    Mainly used in required quantity serializers.
    """

    class Meta:  # noqa: D106
        model = models.Equipment
        fields = ["name_en", "packaging_en", "consumable", "perishable"]


class MoleculeSerializer(serializers.ModelSerializer):
    """Molecule serializer.

    Mainly used in required quantity serializers.
    """

    class Meta:  # noqa: D106
        model = models.Molecule
        fields = ["name_en", "roa", "dosage_form", "composition_en"]


class EquipmentReqQtySerializer(serializers.ModelSerializer):
    """Equipment required quantity serializer."""

    base = EquipmentSerializer()

    class Meta:  # noqa: D106
        model = models.EquipmentReqQty
        fields = ["base", "required_quantity"]


class MoleculeReqQtySerializer(serializers.ModelSerializer):
    """Molecule required quantity serializer."""

    base = MoleculeSerializer(read_only=True)
    # base = serializers.SlugRelatedField()

    class Meta:  # noqa: D106
        model = models.MoleculeReqQty
        fields = ["base", "required_quantity"]


class TelemedicalReqQtySerializer(serializers.ModelSerializer):
    """Telemedical required quantity serializer."""

    base = EquipmentSerializer()

    class Meta:  # noqa: D106
        model = models.TelemedicalReqQty
        fields = ["base", "required_quantity"]


class LaboratoryReqQtySerializer(serializers.ModelSerializer):
    """Laboratory required quantity serializer."""

    base = EquipmentSerializer()

    class Meta:  # noqa: D106
        model = models.LaboratoryReqQty
        fields = ["base", "required_quantity"]


class FirstAidKitReqQtySerializer(serializers.ModelSerializer):
    """First Aid Kit required quantity serializer."""

    required_quantity = serializers.IntegerField()
    content_type = ContentTypeSerializer()
    base = MyGenericRelatedField({
        models.Molecule: MoleculeSerializer(),
        models.Equipment: EquipmentSerializer()
    })

    class Meta:  # noqa: D106
        model = models.FirstAidKitReqQty
        fields = ('required_quantity', 'base', 'content_type')


class RescueBagReqQtySerializer(serializers.ModelSerializer):
    """Rescue Bag required quantity serializer."""

    required_quantity = serializers.IntegerField()
    content_type = ContentTypeSerializer()
    base = GenericRelatedField({
        models.Molecule: MoleculeSerializer(),
        models.Equipment: EquipmentSerializer()
    })

    class Meta:  # noqa: D106
        model = models.RescueBagReqQty
        fields = ('required_quantity', 'base', 'content_type')
