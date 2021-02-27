# -*- coding: utf-8; -*-
"""Test suite for `parsers.equipment` subpackage."""
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
from pharmaship.inventory import parsers


class ParserMethodTestCase(TestCase):
    """Tests for `inventory.parsers` methods.

    Test for Equipment, Molecule, Laboratory and Telemedical parsers.
    First Aid Kits and Rescue Bag parsers have their own test scripts."""

    def setUp(self):  # noqa: D102
        self.assets = Path(settings.BASE_DIR) / "tests/inventory/assets"
        call_command("loaddata", self.assets / "test.dump.yaml")
        self.params = GlobalParameters()

    def test_equipment_parser(self):
        """Check conformity of parser's output.

        Proceed in two steps:
        1. Check the conformity of output items
        2. Check the conformity of output keys

        Use Cerberus for checking conformity.
        """
        output = parsers.equipment.parser(self.params)
        schema_path = settings.VALIDATOR_PATH / "parsers" / "equipment.json"
        schema = json.loads(schema_path.read_text())

        group_type = TypeDefinition(
            name='equipment_group',
            included_types=(models.EquipmentGroup,),
            excluded_types=()
            )
        image_field = TypeDefinition(
            name='image_field',
            included_types=(ImageFieldFile,),
            excluded_types=()
            )
        Validator.types_mapping['equipment_group'] = group_type
        Validator.types_mapping['image_field'] = image_field

        validator = Validator(schema)

        for item in output:
            dict_result = {"data": output[item]}
            result = validator.validate(dict_result)
            if not result:
                log.error(validator.errors)
                log.debug(output[item])
            self.assertTrue(result)

        schema = {
            "data": {
                "type": "dict",
                "keysrules": {
                    "type": "equipment_group"
                }
            }
        }
        validator = Validator(schema)
        self.assertTrue(validator.validate({"data": output}))

    def test_medicine_parser(self):
        """Check conformity of parser's output.

        Proceed in two steps:
        1. Check the conformity of output items
        2. Check the conformity of output keys

        Use Cerberus for checking conformity.
        """
        output = parsers.medicines.parser(self.params)
        schema_path = settings.VALIDATOR_PATH / "parsers" / "medicines.json"
        schema = json.loads(schema_path.read_text())

        group_type = TypeDefinition(
            name='molecule_group',
            included_types=(models.MoleculeGroup,),
            excluded_types=()
            )
        Validator.types_mapping['molecule_group'] = group_type

        validator = Validator(schema)

        for item in output:
            dict_result = {"data": output[item]}
            result = validator.validate(dict_result)
            if not result:
                log.error(validator.errors)
                log.debug(output[item])
            self.assertTrue(result)

        schema = {
            "data": {
                "type": "dict",
                "keysrules": {
                    "type": "molecule_group"
                }
            }
        }
        validator = Validator(schema)
        self.assertTrue(validator.validate({"data": output}))

    def test_laboratory_parser(self):
        """Check conformity of parser's output.

        Proceed in two steps:
        1. Check the conformity of output items
        2. Check the conformity of output keys

        Use Cerberus for checking conformity.
        """
        output = parsers.laboratory.parser(self.params)
        schema_path = settings.VALIDATOR_PATH / "parsers" / "laboratory.json"
        schema = json.loads(schema_path.read_text())

        group_type = TypeDefinition(
            name='equipment_group',
            included_types=(models.EquipmentGroup,),
            excluded_types=()
            )
        image_field = TypeDefinition(
            name='image_field',
            included_types=(ImageFieldFile,),
            excluded_types=()
            )
        Validator.types_mapping['equipment_group'] = group_type
        Validator.types_mapping['image_field'] = image_field

        validator = Validator(schema)

        dict_result = {"data": output}
        result = validator.validate(dict_result)
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)

    def test_telemedical_parser(self):
        """Check conformity of parser's output.

        Proceed in two steps:
        1. Check the conformity of output items
        2. Check the conformity of output keys

        Use Cerberus for checking conformity.
        """
        output = parsers.laboratory.parser(self.params)
        schema_path = settings.VALIDATOR_PATH / "parsers" / "telemedical.json"
        schema = json.loads(schema_path.read_text())

        group_type = TypeDefinition(
            name='equipment_group',
            included_types=(models.EquipmentGroup,),
            excluded_types=()
            )
        image_field = TypeDefinition(
            name='image_field',
            included_types=(ImageFieldFile,),
            excluded_types=()
            )
        Validator.types_mapping['equipment_group'] = group_type
        Validator.types_mapping['image_field'] = image_field

        validator = Validator(schema)

        dict_result = {"data": output}
        result = validator.validate(dict_result)
        if not result:
            log.error(validator.errors)
            log.debug(output)
        self.assertTrue(result)
