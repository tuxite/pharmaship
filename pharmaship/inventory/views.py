# -*- coding: utf-8; -*-
"""Inventory application REST framework viewsets.

These views are not used so far, they are here for debugging purpose using
HTML view provided by Django Rest Framework.
"""
from rest_framework import viewsets

from pharmaship.inventory import models
from pharmaship.inventory import serializers


class MoleculeViewSet(viewsets.ModelViewSet):
    """Molecule viewset"""

    queryset = models.Molecule.objects.all()
    serializer_class = serializers.MoleculeSerializer


class EquipmentViewSet(viewsets.ModelViewSet):
    """Equipment viewset"""

    queryset = models.Equipment.objects.all()
    serializer_class = serializers.EquipmentSerializer


class FirstAidKitReqQtyViewSet(viewsets.ModelViewSet):
    """First Aid Kit required quantity viewset"""

    queryset = models.FirstAidKitReqQty.objects.all()
    serializer_class = serializers.FirstAidKitReqQtySerializer


class RescueBagReqQtyViewSet(viewsets.ModelViewSet):
    """Rescue Bag required quantity viewset"""

    queryset = models.RescueBagReqQty.objects.all()
    serializer_class = serializers.RescueBagReqQtySerializer


class EquipmentReqQtyViewSet(viewsets.ModelViewSet):
    """Equipment required quantity viewset"""

    queryset = models.EquipmentReqQty.objects.all().prefetch_related("base")
    serializer_class = serializers.EquipmentReqQtySerializer


class MoleculeReqQtyViewSet(viewsets.ModelViewSet):
    """Molecule required quantity viewset"""

    queryset = models.MoleculeReqQty.objects.all().prefetch_related("base")
    serializer_class = serializers.MoleculeReqQtySerializer


class TelemedicalReqQtyViewSet(viewsets.ModelViewSet):
    """Telemedical required quantity viewset"""

    queryset = models.TelemedicalReqQty.objects.all().prefetch_related("base")
    serializer_class = serializers.TelemedicalReqQtySerializer


class LaboratoryReqQtyViewSet(viewsets.ModelViewSet):
    """Laboratory required quantity viewset"""

    queryset = models.LaboratoryReqQty.objects.all().prefetch_related("base")
    serializer_class = serializers.LaboratoryReqQtySerializer
