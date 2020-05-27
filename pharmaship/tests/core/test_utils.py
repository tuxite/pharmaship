# -*- coding: utf-8; -*-
"""Test suite for `utils` subpackage."""
from django.test import TestCase

import datetime

from pharmaship.core import utils

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from cerberus import Validator


class UtilsTestCase(TestCase):
    """Tests for `core.utils` methods."""

    def setUp(self):  # noqa: D102
        pass

    def test_remove_yaml_pk(self):
        """Check the Primary Key is removed."""
        # YAML without PK
        input = """
        - model: inventory.molecule
          pk: 5
          fields:
            name: Trinitrine
            roa: 31
            dosage_form: 91
            composition: 0,15 mg/dose
            medicine_list: 2
            group: 1
            tag: []
        - model: inventory.molecule
          pk: 27
          fields:
            name: Phloroglucinol
            roa: 31
            dosage_form: 5
            composition: 80 mg
            medicine_list: 0
            group: 3
            tag: []
        """

        yaml_string = """
        - model: inventory.molecule
          fields:
            name: Trinitrine
            roa: 31
            dosage_form: 91
            composition: 0,15 mg/dose
            medicine_list: 2
            group: 1
            tag: []
        - model: inventory.molecule
          fields:
            name: Phloroglucinol
            roa: 31
            dosage_form: 5
            composition: 80 mg
            medicine_list: 0
            group: 3
            tag: []
        """
        output = load(yaml_string, Loader=Loader)
        raw_result = utils.remove_yaml_pk(input)
        result = load(raw_result, Loader=Loader)
        self.assertEqual(result, output)

    def test_add_months(self):
        """Check proper add of months to a date."""
        input = datetime.date(2020, 1, 31)
        n = 3

        result = datetime.date(2020, 4, 30)

        output = utils.add_months(input, n)
        self.assertEqual(result, output)

    def test_end_of_month(self):
        input = datetime.date(2020, 2, 18)
        result = datetime.date(2020, 2, 29)

        output = utils.end_of_month(input)
        self.assertEqual(result, output)

    def test_get_content_types(self):
        result = utils.get_content_types()
        schema = {
            "data": {
                "type": "dict",
                "keysrules": {
                    "type": "string",
                    "regex": "[a-z]+"
                    },
                "valuesrules": {
                    "type": "integer"
                    }
                }
            }

        validator = Validator(schema)
        dict_result = {"data": result}
        self.assertTrue(validator.validate(dict_result))
