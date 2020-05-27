# -*- coding: utf-8; -*-
"""Inventory application REST framework serializers."""
from rest_framework import serializers
from generic_relations.relations import GenericRelatedField

from django.contrib.contenttypes.models import ContentType

from pharmaship.inventory import models


class MyGenericRelatedField(GenericRelatedField):
    """Customized GenericRelatedField."""
    # def get_deserializer_for_data(self, value):
    #     log.warning(value)


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:  # noqa: D106
        model = ContentType
        fields = ["app_label", "name"]


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:  # noqa: D106
        model = models.Equipment
        fields = ["name", "packaging", "consumable", "perishable"]


class MoleculeSerializer(serializers.ModelSerializer):
    class Meta:  # noqa: D106
        model = models.Molecule
        fields = ["name", "roa", "dosage_form", "composition"]


class EquipmentReqQtySerializer(serializers.ModelSerializer):
    base = EquipmentSerializer()

    class Meta:  # noqa: D106
        model = models.EquipmentReqQty
        fields = ["base", "required_quantity"]


class MoleculeReqQtySerializer(serializers.ModelSerializer):
    base = MoleculeSerializer(read_only=True)
    # base = serializers.SlugRelatedField()

    class Meta:  # noqa: D106
        model = models.MoleculeReqQty
        fields = ["base", "required_quantity"]


class TelemedicalReqQtySerializer(serializers.ModelSerializer):
    base = EquipmentSerializer()

    class Meta:  # noqa: D106
        model = models.TelemedicalReqQty
        fields = ["base", "required_quantity"]


class LaboratoryReqQtySerializer(serializers.ModelSerializer):
    base = EquipmentSerializer()

    class Meta:  # noqa: D106
        model = models.LaboratoryReqQty
        fields = ["base", "required_quantity"]


class FirstAidKitReqQtySerializer(serializers.ModelSerializer):
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
    required_quantity = serializers.IntegerField()
    content_type = ContentTypeSerializer()
    base = GenericRelatedField({
        models.Molecule: MoleculeSerializer(),
        models.Equipment: EquipmentSerializer()
    })

    class Meta:  # noqa: D106
        model = models.RescueBagReqQty
        fields = ('required_quantity', 'base', 'content_type')
