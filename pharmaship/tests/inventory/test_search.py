# -*- coding: utf-8; -*-
"""Test suite for `search` subpackage."""
import json

from pathlib import Path

from django.test import TestCase
from django.conf import settings

from django.core.management import call_command

from cerberus import Validator  # , TypeDefinition

from pharmaship.core.utils import log
from pharmaship.gui.view import GlobalParameters

from pharmaship.inventory import search

from pharmaship.inventory import models


class UtilsTestCase(TestCase):
    """Tests for `inventory.utils` methods."""

    def setUp(self):  # noqa: D102
        self.assets = Path(settings.BASE_DIR) / "tests/inventory/assets"

    # def test_filepath(self):
    #     """Check the "slugification"."""
    #     class Dummy:
    #         name = "Test"
    #
    #     obj = Dummy()
    #     obj.name = "This is a text with details 90*60 !&&"
    #     filename = "inventory/picture/dummy_filename.png"
    #     output = "this-is-a-text-with-details-9060.png"
    #
    #     res = utils.filepath(obj, filename)
    #     self.assertEqual(res, output)

    def test_location_display(self):
        call_command("loaddata", self.assets / "locations.yaml")

        params = GlobalParameters()
        locations = params.locations

        location_id_list = [9, 10]
        result = search.location_display(location_id_list, locations)

        expected_result = [
            'Location A > Location C > Bag One',
            'Location B > Location 3b'
            ]
        self.assertEqual(result, expected_result)

    def test_get_quantity(self):
        call_command("loaddata", self.assets / "search_transactions.yaml")

        medicine = models.Medicine.objects.get(id=1)
        transactions = medicine.transactions.all().order_by("date")

        result = search.get_quantity(transactions)

        expected_result = 17
        self.assertEqual(result, expected_result)

    def test_get_molecules(self):
        call_command("loaddata", self.assets / "test.dump.yaml")
        text = "Doli"
        params = GlobalParameters()
        output = search.get_molecules(text, params)

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "search.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        result = validator.validate({"data": output})
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_get_equipments(self):
        call_command("loaddata", self.assets / "test.dump.yaml")
        text = "Doli"
        params = GlobalParameters()
        output = search.get_equipments(text, params)

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "search.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        result = validator.validate({"data": output})
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_search(self):
        call_command("loaddata", self.assets / "test.dump.yaml")
        text = "Doli"
        params = GlobalParameters()
        output = search.search(text, params)

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "search.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        result = validator.validate({"data": output})
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_parse_items(self):
        call_command(
            "loaddata",
            self.assets / "locations.yaml",
            self.assets / "search_parse_items.yaml",
            )

        items = []
        output = search.parse_items(items)

        schema = {
            "data": {
                "type": "list",
                "items": [
                    {
                        "type": "list",
                        "schema": {
                            "type": "integer",
                            "min": 0
                        }
                    },
                    {
                        "type": "dict",
                        "keysrules": {
                            "type": "integer",
                            "min": 0
                        },
                        "valuesrules": {
                            "type": "integer",
                            "min": 0
                        }
                    }
                ]
            }
        }
        validator = Validator(schema)

        result = validator.validate({"data": output})
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)
