# -*- coding: utf-8; -*-
"""Test suite for `import_data` subpackage."""
import tarfile
import datetime

from pathlib import Path

from django.test import TestCase
from django.core.management import call_command
from django.conf import settings

from pharmaship.core.utils import log
from pharmaship.core.config import read_config
from pharmaship.inventory import import_data
from pharmaship.inventory import models


class ImportMethodTestCase(TestCase):
    """Tests for `inventory.import_data` methods."""

    def setUp(self):  # noqa: D102
        self.assets = Path(settings.BASE_DIR) / "tests/inventory/assets"

    def test_picture_files(self):
        tar_filename = self.assets / "picture_file.tar"

        allowed_files = ["fileA.txt", "fileB.txt"]

        tar_file = tarfile.open(tar_filename)
        for item in import_data.pictures_files(tar_file):
            self.assertIn(item.name, allowed_files)

    def test_get_file(self):
        tar_filename = self.assets / "picture_file.tar"
        tar_file = tarfile.open(tar_filename)

        filename = "fileC.txt"
        content = b"This is a test file.\n"

        output = import_data.get_file(filename, tar_file)
        self.assertEqual(content, output)

        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(import_data.get_file("wrong_file.dat", tar_file))
        for item in cm.output:
            self.assertIn("File `wrong_file.dat` not found.", item)

    def test_get_model(self):
        from django.contrib.contenttypes.models import ContentType

        data = {
            "app_label": "inventory",
            "name": "medicine"
        }

        output = import_data.get_model(data)
        self.assertIsInstance(output, ContentType)

        data = {
            "app_label": "inventory",
            "name": "medicines"
        }
        with self.assertLogs(log, level='ERROR') as cm:
            output = import_data.get_model(data)
            self.assertIsNone(output)
        for item in cm.output:
            self.assertIn("ContentType not found.", item)

    def test_get_base(self):
        content = {
          "name": "Glucose",
          "roa": 5,
          "dosage_form": 50,
          "composition": "5% - 500 mL"
        }

        base_type = models.MoleculeReqQty

        with self.assertLogs(log, level='ERROR') as cm:
            output = import_data.get_base(base_type, content)
            self.assertIsNone(output)
        for item in cm.output:
            self.assertIn("Model class not found:", item)

        base_type = models.MoleculeReqQty.base

        with self.assertLogs(log, level='ERROR') as cm:
            output = import_data.get_base(base_type, content)
            self.assertIsNone(output)
        for item in cm.output:
            self.assertIn("instance does not exist", item)

        models.MoleculeGroup.objects.create(
            id=1,
            name="Test",
            order=1
            )

        instance = models.Molecule.objects.create(
            medicine_list=0,
            group_id=1,
            **content
        )
        output = import_data.get_base(base_type, content)
        self.assertEqual(output, instance)

    def test_deserialize_json_file(self):
        tar_filename = self.assets / "json_serialize.tar"
        tar_file = tarfile.open(tar_filename)

        data = {
            "filename": "bad_molecule.json",
            "model": models.FirstAidKitReqQty
        }

        allowance = models.Allowance.objects.create(
            name="Allowance Test",
            author="Pharmaship test",
            signature="a",
            date=datetime.datetime.now(),
            version="Vertest",
            additional=False,
            active=True
        )

        call_command("loaddata", self.assets / "deserialize_test.yaml")

        with self.assertLogs(log, level='ERROR') as cm:
            output = import_data.deserialize_json_file(
                data,
                tar_file,
                allowance
                )
            self.assertFalse(output)
        log_check = False
        for item in cm.output:
            if "Base for item not found." in item:
                log_check = True
        self.assertTrue(log_check)

        data["filename"] = "good_molecule.json"

        output = import_data.deserialize_json_file(data, tar_file, allowance)
        self.assertEqual(len(output), 3)
        for item in output:
            self.assertIsInstance(item, data["model"])

    def test_required_quantity(self):
        call_command("loaddata", self.assets / "deserialize_test.yaml")

        tar_filename = self.assets / "json_serialize.tar"
        tar_file = tarfile.open(tar_filename)

        data = {
            "filename": "bad_molecule.json",
            "model": models.FirstAidKitReqQty
        }

        allowance = models.Allowance.objects.create(
            name="Allowance Test",
            author="Pharmaship test",
            signature="a",
            date=datetime.datetime.now(),
            version="Vertest",
            additional=False,
            active=True
        )

        with self.assertLogs(log, level='ERROR') as cm:
            output = import_data.required_quantity(data, tar_file, allowance)
            self.assertFalse(output)
        item = cm.output[-1]
        self.assertIn("Error when deserializing file:", item)

        data["filename"] = "good_molecule.json"
        with self.assertLogs(log, level='DEBUG'):
            output = import_data.required_quantity(data, tar_file, allowance)
            self.assertTrue(output)


class ImportClassTestCase(TestCase):
    """Tests for `inventory.import_data.DataImport` class."""

    def setUp(self):  # noqa: D102
        self.assets = Path(settings.BASE_DIR) / "tests/inventory/assets"
        self.conf = read_config()
        self.key = {"keyid": "0123456789abcdef"}

    def test_import_allowance(self):
        # Empty file
        tar_filename = self.assets / "update_bad_allowance.tar"
        tar_file = tarfile.open(tar_filename)
        cls = import_data.DataImport(tar_file, self.conf, self.key)

        self.assertFalse(cls.import_allowance())

        # Corrupted file
        tar_filename = self.assets / "update_bad_allowance2.tar"
        tar_file = tarfile.open(tar_filename)
        cls = import_data.DataImport(tar_file, self.conf, self.key)

        with self.assertLogs(log, level='ERROR') as cm:
            output = cls.import_allowance()
            self.assertFalse(output)
        item = cm.output[-1]
        self.assertIn("Cannot deserialize allowance:", item)

        # Correct result
        tar_filename = self.assets / "update_bad_molecule.tar"
        tar_file = tarfile.open(tar_filename)
        cls = import_data.DataImport(tar_file, self.conf, self.key)

        with self.assertLogs(log, level='DEBUG'):
            output = cls.import_allowance()
            self.assertIsInstance(output, models.Allowance)

    def test_import_molecule(self):
        call_command(
            "loaddata",
            settings.PHARMASHIP_DATA / "MoleculeGroup.yaml"
            )

        # Empty file
        tar_filename = self.assets / "update_bad_molecule.tar"
        tar_file = tarfile.open(tar_filename)
        cls = import_data.DataImport(tar_file, self.conf, self.key)

        self.assertFalse(cls.import_molecule())

        # Corrupted file
        tar_filename = self.assets / "update_bad_molecule2.tar"
        tar_file = tarfile.open(tar_filename)
        cls = import_data.DataImport(tar_file, self.conf, self.key)

        with self.assertLogs(log, level='ERROR') as cm:
            output = cls.import_molecule()
            self.assertFalse(output)
        item = cm.output[-1]
        self.assertIn("Cannot deserialize molecule objects:", item)

        # Correct result
        tar_filename = self.assets / "update_bad_equipment.tar"
        tar_file = tarfile.open(tar_filename)
        cls = import_data.DataImport(tar_file, self.conf, self.key)

        with self.assertLogs(log, level='DEBUG'):
            output = cls.import_molecule()
            self.assertTrue(output)

    def test_import_equipment(self):
        call_command(
            "loaddata",
            settings.PHARMASHIP_DATA / "EquipmentGroup.yaml"
            )

        # Empty file
        tar_filename = self.assets / "update_bad_equipment.tar"
        tar_file = tarfile.open(tar_filename)
        cls = import_data.DataImport(tar_file, self.conf, self.key)

        self.assertFalse(cls.import_equipment())

        # Corrupted file
        tar_filename = self.assets / "update_bad_equipment2.tar"
        tar_file = tarfile.open(tar_filename)
        cls = import_data.DataImport(tar_file, self.conf, self.key)

        with self.assertLogs(log, level='ERROR') as cm:
            output = cls.import_equipment()
            self.assertFalse(output)
        item = cm.output[-1]
        self.assertIn("Cannot deserialize equipment objects:", item)

        # Correct result
        tar_filename = self.assets / "update_all_good.tar"
        tar_file = tarfile.open(tar_filename)
        cls = import_data.DataImport(tar_file, self.conf, self.key)

        with self.assertLogs(log, level='DEBUG'):
            output = cls.import_equipment()
            self.assertTrue(output)

    def test_update(self):
        call_command(
            "loaddata",
            settings.PHARMASHIP_DATA / "Allowance.yaml"
            )
        call_command(
            "loaddata",
            settings.PHARMASHIP_DATA / "MoleculeGroup.yaml"
            )
        call_command(
            "loaddata",
            settings.PHARMASHIP_DATA / "EquipmentGroup.yaml"
            )

        # Verify the first part (YAML files)
        bad_yaml_archives = [
            "update_bad_allowance.tar",
            "update_bad_allowance2.tar",
            "update_bad_molecule.tar",
            "update_bad_molecule2.tar",
            "update_bad_equipment.tar",
            "update_bad_equipment2.tar"
        ]

        for tar_filename in bad_yaml_archives:
            tar_file = tarfile.open(self.assets / tar_filename)
            cls = import_data.DataImport(tar_file, self.conf, self.key)
            with self.assertLogs(log):
                output = cls.update()
                self.assertFalse(output)

        # Check for JSON files
        bad_json_archives = [
            "update_bad_required_qty_01_corrupted.tar",
            "update_bad_required_qty_02_empty.tar",
            "update_bad_required_qty_03_missing.tar",
        ]

        for tar_filename in bad_json_archives:
            tar_file = tarfile.open(self.assets / tar_filename)
            cls = import_data.DataImport(tar_file, self.conf, self.key)
            with self.assertLogs(log):
                output = cls.update()
                self.assertFalse(output)

        # Correct result
        tar_filename = self.assets / "update_all_good.tar"
        tar_file = tarfile.open(tar_filename)
        cls = import_data.DataImport(tar_file, self.conf, self.key)

        with self.assertLogs(log, level='DEBUG'):
            output = cls.update()
            self.assertTrue(output)
