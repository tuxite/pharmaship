"""Pharmaship Inventory URL configuration."""
from django.urls import path, include
from rest_framework import routers

from pharmaship.inventory import views

router = routers.DefaultRouter()
router.register(r'molecules', views.MoleculeViewSet)
router.register(r'equipments', views.EquipmentViewSet)
router.register(r'required/molecule', views.MoleculeReqQtyViewSet)
router.register(r'required/equipment', views.EquipmentReqQtyViewSet)
router.register(r'required/first-aid-kit', views.FirstAidKitReqQtyViewSet)
router.register(r'required/rescue-bag', views.RescueBagReqQtyViewSet)
router.register(r'required/laboratory', views.LaboratoryReqQtyViewSet)
router.register(r'required/telemedical', views.TelemedicalReqQtyViewSet)

urlpatterns = [
    path(r'', include(router.urls)),
]
