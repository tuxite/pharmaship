# -*- coding: utf-8; -*-
"""Test suite for `utils` subpackage."""
import json

from pathlib import Path

from django.test import TestCase
from django.conf import settings

from django.core.management import call_command

from cerberus import Validator  # , TypeDefinition

from pharmaship.core.utils import log
from pharmaship.inventory import utils

from pharmaship.inventory import models


class UtilsTestCase(TestCase):
    """Tests for `inventory.utils` methods."""

    def setUp(self):  # noqa: D102
        self.assets = Path(settings.BASE_DIR) / "tests/inventory/assets"

    def test_filepath(self):
        """Check the "slugification"."""
        class Dummy:
            name = "Test"

        obj = Dummy()
        obj.name = "This is a text with details 90*60 !&&"
        filename = "inventory/picture/dummy_filename.png"
        output = "this-is-a-text-with-details-9060.png"

        res = utils.filepath(obj, filename)
        self.assertEqual(res, output)

    def test_get_location_list(self):
        raw_schema = (settings.VALIDATOR_PATH / "location_list.json").read_text()

        try:
            schema = json.loads(raw_schema)
        except (ValueError, TypeError) as error:
            log.error("Unable to parse the schema file. %s", error)
            return False

        # # Add custom Location type for validator
        # location_type = TypeDefinition('location', (Location,), ())
        # Validator.types_mapping['location'] = location_type

        validator = Validator(schema)

        call_command("loaddata", self.assets / "locations.yaml")

        result = utils.get_location_list()
        dict_result = {"data": result}
        self.assertTrue(validator.validate(dict_result))

    def test_req_qty_element(self):
        """Check result from a specific dataset."""
        call_command("loaddata", self.assets / "req_qty_test.yaml")
        allowances = models.Allowance.objects.filter(active=True)
        req_qty_list = models.MoleculeReqQty.objects.filter(
            allowance__in=allowances
            )

        element = models.Molecule.objects.get(id=1)
        total_quantity, detail = utils.req_qty_element(element, req_qty_list)
        self.assertEqual(total_quantity, 150)
        self.assertEqual(len(detail), 3)

        element = models.Molecule.objects.get(id=2)
        total_quantity, detail = utils.req_qty_element(element, req_qty_list)
        self.assertEqual(total_quantity, 25)
        self.assertEqual(len(detail), 1)

        element = models.Molecule.objects.get(id=3)
        total_quantity, detail = utils.req_qty_element(element, req_qty_list)
        self.assertEqual(total_quantity, 0)
