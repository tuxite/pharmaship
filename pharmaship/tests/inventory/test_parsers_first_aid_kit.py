# -*- coding: utf-8; -*-
"""Test suite for `parsers.first_aid` subpackage."""
import json
from pathlib import Path

from django.test import TestCase
from django.core.management import call_command
from django.conf import settings
from django.db.models.fields.files import ImageFieldFile
from cerberus import Validator, TypeDefinition

from pharmaship.core.utils import log
from pharmaship.gui.view import GlobalParameters
from pharmaship.inventory import models
from pharmaship.inventory.parsers import first_aid


class ParserMethodTestCase(TestCase):
    """Tests for `inventory.parsers.first_aid` methods."""

    def setUp(self):  # noqa: D102
        self.assets = Path(settings.BASE_DIR) / "tests/inventory/assets"
        # call_command("loaddata", self.assets / "test.dump.yaml")
        call_command(
            "loaddata",
            self.assets / "parsers" / "first_aid_kit.yaml"
            )
        self.params = GlobalParameters()

    def test_get_required(self):
        output = first_aid.get_required(self.params)

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "first_aid",
            "get_required.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        result = validator.validate(output)
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_get_transactions(self):
        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "first_aid",
            "get_transactions.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        # Test for medicines
        content_type = self.params.content_types["medicine"]
        items = models.Medicine.objects.filter(
            used=False).values_list("id", flat=True)
        output = first_aid.get_transactions(content_type, items)
        result = validator.validate({"data": output})
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

        # Test for articles
        content_type = self.params.content_types["article"]
        items = models.Article.objects.filter(
            used=False).values_list("id", flat=True)
        output = first_aid.get_transactions(content_type, items)
        result = validator.validate({"data": output})
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_create_molecule(self):
        required = first_aid.get_required(self.params)
        molecule = models.Molecule.objects.get(id=3)

        output = first_aid.create_molecule(
            item=molecule,
            content_type=self.params.content_types["molecule"],
            required=required["molecules"]
            )

        image_field = TypeDefinition(
            name='image_field',
            included_types=(ImageFieldFile,),
            excluded_types=()
            )
        Validator.types_mapping['image_field'] = image_field

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "first_aid",
            "single_item.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        result = validator.validate(output)
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_create_equipment(self):
        required = first_aid.get_required(self.params)
        equipment = models.Equipment.objects.get(id=2)

        output = first_aid.create_equipment(
            item=equipment,
            content_type=self.params.content_types["equipment"],
            required=required["equipments"]
            )

        image_field = TypeDefinition(
            name='image_field',
            included_types=(ImageFieldFile,),
            excluded_types=()
            )
        Validator.types_mapping['image_field'] = image_field

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "first_aid",
            "single_item.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        result = validator.validate(output)
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_get_available_medicines(self):
        element = models.Molecule.objects.get(pk=1)
        items_id_list = element.medicines.all().values_list("id", flat=True)

        transactions = first_aid.get_transactions(
            content_type=self.params.content_types["medicine"],
            items=items_id_list
            )

        output = first_aid.get_available_medicines(
            element=element,
            content_type_id=self.params.content_types["medicine"],
            qty_transactions=transactions
            )

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "first_aid",
            "available_items.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)
        result = validator.validate({"data": output})
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_get_available_articles(self):
        element = models.Equipment.objects.get(pk=1)
        items_id_list = element.articles.all().values_list("id", flat=True)

        transactions = first_aid.get_transactions(
            content_type=self.params.content_types["article"],
            items=items_id_list
            )

        output = first_aid.get_available_articles(
            element=element,
            content_type_id=self.params.content_types["article"],
            qty_transactions=transactions
            )

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "first_aid",
            "available_items.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)
        result = validator.validate({"data": output})
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_merge_elements(self):
        data = {
            "molecules": {
                1: "A",
                2: "B"
            },
            "equipments": {
                11: "C",
                22: "D"
            }
        }

        expected_result = ["A", "B", "C", "D"]
        output = first_aid.merge_elements(data)
        self.assertEqual(expected_result, output)

    def test_get_subitems(self):
        kit = models.FirstAidKit.objects.get(pk=1)
        dummy_common = {
            "molecules": {
                1: {
                    "exp_dates": [],
                    "quantity": 0,
                    "expiring_quantity": 0,
                    "contents": [],
                    "has_nc": False,
                    "has_date_warning": False,
                    "has_date_expired": False
                },
                2: {
                    "exp_dates": [],
                    "quantity": 0,
                    "expiring_quantity": 0,
                    "contents": [],
                    "has_nc": False,
                    "has_date_warning": False,
                    "has_date_expired": False
                },
                3: {
                    "exp_dates": [],
                    "quantity": 0,
                    "expiring_quantity": 0,
                    "contents": [],
                    "has_nc": False,
                    "has_date_warning": False,
                    "has_date_expired": False
                }
            },
            "equipments": {
                1: {
                    "exp_dates": [],
                    "quantity": 0,
                    "expiring_quantity": 0,
                    "contents": [],
                    "has_nc": False,
                    "has_date_warning": False,
                    "has_date_expired": False
                },
                2: {
                    "exp_dates": [],
                    "quantity": 0,
                    "expiring_quantity": 0,
                    "contents": [],
                    "has_nc": False,
                    "has_date_warning": False,
                    "has_date_expired": False
                },
                3: {
                    "exp_dates": [],
                    "quantity": 0,
                    "expiring_quantity": 0,
                    "contents": [],
                    "has_nc": False,
                    "has_date_warning": False,
                    "has_date_expired": False
                }
            }
        }

        output = first_aid.get_subitems(self.params, kit, dummy_common)

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "first_aid",
            "subitems.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)
        result = validator.validate({"data": output})
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_parser(self):
        kits = models.FirstAidKit.objects.all()
        output = first_aid.parser(self.params, kits)

        self.assertIsInstance(output, list)

        image_field = TypeDefinition(
            name='image_field',
            included_types=(ImageFieldFile,),
            excluded_types=()
            )
        Validator.types_mapping['image_field'] = image_field

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "first_aid",
            "first_aid_kit.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)
        for item in output:
            result = validator.validate(item)
            if not result:
                log.error(validator.errors)
                log.debug(item)
            self.assertTrue(result)
