# -*- coding: utf-8; -*-
"""Test suite for `parsers.rescue_bag` subpackage."""
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
from pharmaship.inventory.parsers import rescue_bag


class ParserMethodTestCase(TestCase):
    """Tests for `inventory.parsers.rescue_bag` methods."""

    def setUp(self):  # noqa: D102
        self.assets = Path(settings.BASE_DIR) / "tests/inventory/assets"
        # call_command("loaddata", self.assets / "test.dump.yaml")
        call_command(
            "loaddata",
            self.assets / "parsers" / "rescue_bag.yaml"
            )
        self.params = GlobalParameters()

    def test_get_required(self):
        output = rescue_bag.get_required(self.params)

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "rescue_bag",
            "get_required.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        result = validator.validate(output)
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_create_molecule(self):

        required = rescue_bag.get_required(self.params)
        molecule = models.Molecule.objects.get(id=3)

        output = rescue_bag.create_molecule(molecule, required["molecules"])

        image_field = TypeDefinition(
            name='image_field',
            included_types=(ImageFieldFile,),
            excluded_types=()
            )
        Validator.types_mapping['image_field'] = image_field

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "rescue_bag",
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

        required = rescue_bag.get_required(self.params)
        equipment = models.Equipment.objects.get(id=2)

        output = rescue_bag.create_equipment(equipment, required["equipments"])

        image_field = TypeDefinition(
            name='image_field',
            included_types=(ImageFieldFile,),
            excluded_types=()
            )
        Validator.types_mapping['image_field'] = image_field

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "rescue_bag",
            "single_item.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        result = validator.validate(output)
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_create_molecules(self):
        required = rescue_bag.get_required(self.params)

        output = rescue_bag.create_molecules(
            required["molecules"].keys(),
            required["molecules"]
            )

        image_field = TypeDefinition(
            name='image_field',
            included_types=(ImageFieldFile,),
            excluded_types=()
            )
        Validator.types_mapping['image_field'] = image_field

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "rescue_bag",
            "single_item.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        for item in output:
            result = validator.validate(output[item])
            if not result:
                log.error(validator.errors)
                log.debug(output[item])
            self.assertTrue(result)

        schema = {
            "data": {
                "type": "dict",
                "keysrules": {
                    "type": "integer"
                }
            }
        }
        validator = Validator(schema)
        self.assertTrue(validator.validate({"data": output}))

    def test_create_equipments(self):
        required = rescue_bag.get_required(self.params)

        output = rescue_bag.create_equipments(
            required["equipments"].keys(),
            required["equipments"]
            )

        image_field = TypeDefinition(
            name='image_field',
            included_types=(ImageFieldFile,),
            excluded_types=()
            )
        Validator.types_mapping['image_field'] = image_field

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "rescue_bag",
            "single_item.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        for item in output:
            result = validator.validate(output[item])
            if not result:
                log.error(validator.errors)
                log.debug(output[item])
            self.assertTrue(result)

        schema = {
            "data": {
                "type": "dict",
                "keysrules": {
                    "type": "integer"
                }
            }
        }
        validator = Validator(schema)
        self.assertTrue(validator.validate({"data": output}))

    def test_get_transactions(self):
        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "rescue_bag",
            "get_transactions.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        # Test for medicines
        content_type = self.params.content_types["medicine"]
        items = models.Medicine.objects.filter(used=False).values_list("id", flat=True)
        output = rescue_bag.get_transactions(content_type, items)
        result = validator.validate({"data": output})
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

        # Test for articles
        content_type = self.params.content_types["article"]
        items = models.Article.objects.filter(used=False).values_list("id", flat=True)
        output = rescue_bag.get_transactions(content_type, items)
        result = validator.validate({"data": output})
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_get_medicines(self):
        required = rescue_bag.get_required(self.params)

        output = rescue_bag.get_medicines(
            self.params,
            required["molecules"],
            [100,]
            )

        image_field = TypeDefinition(
            name='image_field',
            included_types=(ImageFieldFile,),
            excluded_types=()
            )
        Validator.types_mapping['image_field'] = image_field

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "rescue_bag",
            "single_item.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        for item in output:
            result = validator.validate(output[item])
            if not result:
                log.error(validator.errors)
                log.debug(output[item])
            self.assertTrue(result)

        schema = {
            "data": {
                "type": "dict",
                "keysrules": {
                    "type": "integer"
                }
            }
        }
        validator = Validator(schema)
        self.assertTrue(validator.validate({"data": output}))

    def test_get_articles(self):
        required = rescue_bag.get_required(self.params)

        output = rescue_bag.get_articles(
            self.params,
            required["equipments"],
            [100,]
            )

        image_field = TypeDefinition(
            name='image_field',
            included_types=(ImageFieldFile,),
            excluded_types=()
            )
        Validator.types_mapping['image_field'] = image_field

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "rescue_bag",
            "single_item.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        for item in output:
            result = validator.validate(output[item])
            if not result:
                log.error(validator.errors)
                log.debug(output[item])
            self.assertTrue(result)

        schema = {
            "data": {
                "type": "dict",
                "keysrules": {
                    "type": "integer"
                }
            }
        }
        validator = Validator(schema)
        self.assertTrue(validator.validate({"data": output}))

    def test_merge_bags(self):
        required = rescue_bag.get_required(self.params)

        equipments = rescue_bag.get_articles(
            self.params,
            required["equipments"],
            [110, 111]
            )

        molecules = rescue_bag.get_medicines(
            self.params,
            required["molecules"],
            [110, 111]
            )

        bags = models.RescueBag.objects.all()

        output = rescue_bag.merge_bags(bags, molecules, equipments)

        image_field = TypeDefinition(
            name='image_field',
            included_types=(ImageFieldFile,),
            excluded_types=()
            )
        Validator.types_mapping['image_field'] = image_field

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "rescue_bag",
            "merged_bags.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        result = validator.validate({"data": output})
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_parser(self):
        output = rescue_bag.parser(self.params)

        image_field = TypeDefinition(
            name='image_field',
            included_types=(ImageFieldFile,),
            excluded_types=()
            )
        Validator.types_mapping['image_field'] = image_field

        schema_path = settings.VALIDATOR_PATH.joinpath(
            "parsers",
            "rescue_bag",
            "rescue_bag.json"
            )
        schema = json.loads(schema_path.read_text())
        validator = Validator(schema)

        result = validator.validate({"data": output})
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)
