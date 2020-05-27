"""Pharmaship URL configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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
