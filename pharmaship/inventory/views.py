# -*- coding: utf-8; -*-
"""Inventory application REST framework viewsets."""
from rest_framework import viewsets

from pharmaship.inventory import models
from pharmaship.inventory import serializers


class MoleculeViewSet(viewsets.ModelViewSet):
    queryset = models.Molecule.objects.all()
    serializer_class = serializers.MoleculeSerializer


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = models.Equipment.objects.all()
    serializer_class = serializers.EquipmentSerializer


class FirstAidKitReqQtyViewSet(viewsets.ModelViewSet):
    queryset = models.FirstAidKitReqQty.objects.all()
    serializer_class = serializers.FirstAidKitReqQtySerializer


class RescueBagReqQtyViewSet(viewsets.ModelViewSet):
    queryset = models.RescueBagReqQty.objects.all()
    serializer_class = serializers.RescueBagReqQtySerializer


class EquipmentReqQtyViewSet(viewsets.ModelViewSet):
    queryset = models.EquipmentReqQty.objects.all().prefetch_related("base")
    serializer_class = serializers.EquipmentReqQtySerializer


class MoleculeReqQtyViewSet(viewsets.ModelViewSet):
    queryset = models.MoleculeReqQty.objects.all().prefetch_related("base")
    serializer_class = serializers.MoleculeReqQtySerializer


class TelemedicalReqQtyViewSet(viewsets.ModelViewSet):
    queryset = models.TelemedicalReqQty.objects.all().prefetch_related("base")
    serializer_class = serializers.TelemedicalReqQtySerializer


class LaboratoryReqQtyViewSet(viewsets.ModelViewSet):
    queryset = models.LaboratoryReqQty.objects.all().prefetch_related("base")
    serializer_class = serializers.LaboratoryReqQtySerializer
