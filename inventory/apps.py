# -*- coding: utf-8 -*-
from django.apps import AppConfig

import models

class InventoryConfig(AppConfig):
    name = 'inventory'
    verbose_name = "Medical"

    # Orderable objects
    def orderable(self):
        """Returns a list of orderable elements."""
        return [
            {'object':models.Equipment, 'name': "Equipment"},
            {'object':models.Molecule, 'name': "Molecule"},
            ]
