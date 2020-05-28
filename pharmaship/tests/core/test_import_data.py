# -*- coding: utf-8; -*-
"""Test suite for `import_data` subpackage."""
from django.test import TestCase
from django.conf import settings

import io
import tarfile
from pathlib import Path

from pharmaship.core.utils import log

from pharmaship.core import import_data


def remove_keyring(path):
    """Remove the specially created keyring if any."""
    for item in path.iterdir():
        if item.is_dir():
            remove_keyring(item)
        else:
            item.unlink(missing_ok=True)
    path.rmdir()


class ImportDataMethodsTestCase(TestCase):
    """Tests for `core.import_data` methods."""

    def setUp(self):  # noqa: D102
        path = Path(settings.BASE_DIR) / "tests/core/keyring"
        self.addCleanup(remove_keyring, path)

        settings.KEYRING_PATH = path
        path.mkdir(parents=True, exist_ok=True)

        self.importer = import_data.Importer()

        self.assets = Path(settings.BASE_DIR) / "tests/core/assets"

    def test_extract_manifest(self):
        """Check the manifest is correctly parsed."""
        # Bad manifest
        manifest = self.assets / "bad_format_manifest"
        manifest_obj = manifest.open('rb')

        with self.assertLogs(log, level='ERROR') as cm:
            result = import_data.extract_manifest(manifest_obj)
            self.assertEqual(result, [])
        for item in cm.output:
            self.assertIn("Unable to read MANIFEST:", item)

        # Good manifest
        manifest = self.assets / "good_manifest"
        manifest_obj = manifest.open('rb')
        self.assertIsInstance(result, list)

    def test_check_tarfile(self):
        """Check that a corrupted tarfile is handled."""

        # Corrupted tar file
        corrupted_data = (self.assets / "corrupted_tar.tar").read_bytes()

        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(import_data.check_tarfile(corrupted_data))
        for item in cm.output:
            self.assertIn("File is not a valid Tar file.", item)

        # Good tar file
        data = (self.assets / "good_tar.tar").read_bytes()
        result = import_data.check_tarfile(data)
        self.assertIsInstance(result, tarfile.TarFile)

    def test_check_integrity(self):
        """Verify that tarfile integrity check handles incoherent content."""
        # No MANIFEST
        tar_obj = tarfile.TarFile(name=self.assets / "no_manifest.tar")
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(import_data.check_integrity(tar_obj))
        for item in cm.output:
            self.assertIn("MANIFEST not found.", item)

        # File in the MANIFEST but not in the tar file
        tar_obj = tarfile.TarFile(name=self.assets / "file_declaration.tar")
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(import_data.check_integrity(tar_obj))
        for item in cm.output:
            self.assertIn("File not in the tar file: dummy", item)

        # Wrong hash
        tar_obj = tarfile.TarFile(name=self.assets / "wrong_hash.tar")
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(import_data.check_integrity(tar_obj))
        for item in cm.output:
            self.assertIn("File corrupted: package.yaml", item)

    def test_load_module(self):
        """Check Pharmaship module import."""
        # Non existing module
        test_module = "my false import as test"
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(import_data.load_module(test_module))
        for item in cm.output:
            self.assertIn(
                "Module my false import as test has no import_data function.",
                item)

        # Existing module but no import_data
        test_module = "gui"
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(import_data.load_module(test_module))
        for item in cm.output:
            self.assertIn("Module gui has no import_data function.", item)

        # Existing module.import_data but not DataImport
        test_module = "tests.core.assets"
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(import_data.load_module(test_module))
        for item in cm.output:
            self.assertIn(
                "Module tests.core.assets has no DataImport class.",
                item)


class ImportDataImporterTestCase(TestCase):
    """Tests for `core.import_data` Importer class."""

    def setUp(self):  # noqa: D102
        path = Path(settings.BASE_DIR) / "tests/core/keyring"
        self.addCleanup(remove_keyring, path)

        settings.KEYRING_PATH = path
        path.mkdir(parents=True, exist_ok=True)

        self.importer = import_data.Importer()

        self.assets = Path(settings.BASE_DIR) / "tests/core/assets"

        self.importer = import_data.Importer()

    def test_read_package(self):
        """Check the ability to read packages."""
        filename = self.assets / "not_existing_file"

        # Not a correct type of argument
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(self.importer.read_package([filename]))
        for item in cm.output:
            self.assertIn(
                "Filename instance not compatible! What is this?!!",
                item)

        # Non-readable file
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(self.importer.read_package(filename))
        for item in cm.output:
            self.assertIn(
                "File impossible to read.",
                item)

        # Unicode error
        filename = self.assets / "corrupted_tar.tar"
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(self.importer.read_package(filename))
        for item in cm.output:
            self.assertIn(
                "File impossible to read (not an ASCII file).",
                item)

        # Correct loading
        filename = self.assets / "unknown_signature.tar.asc"
        self.assertTrue(self.importer.read_package(filename))

        # TextIOWrapper
        content = io.BytesIO(b"some pure ASCII data")
        filename = io.TextIOWrapper(content)
        self.assertTrue(self.importer.read_package(filename))

        content = io.BytesIO(bytes.fromhex('2Ef0 F1f2  '))
        filename = io.TextIOWrapper(content)
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(self.importer.read_package(filename))
        for item in cm.output:
            self.assertIn(
                "File impossible to read (not an ASCII file).",
                item)

    def test_check_signature(self):
        """Check the result of the method."""
        filename = self.assets / "unknown_signature.tar.asc"
        self.assertTrue(self.importer.read_package(filename))

        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(self.importer.check_signature())
        for item in cm.output:
            self.assertIn(
                "Error during signature check:",
                item)

        filename = self.assets / "good_signature.tar.asc"
        self.assertTrue(self.importer.read_package(filename))

        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(self.importer.check_signature())
        for item in cm.output:
            self.assertIn(
                "Error during signature check:",
                item)

    def test_check_conformity(self):
        """Verify every steps of conformity checks."""
        # Not a valid tar file
        asset = self.assets / "corrupted_tar.tar"
        self.importer.data = asset.read_bytes()

        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(self.importer.check_conformity())

        # Wrong manifest
        asset = self.assets / "file_declaration.tar"
        self.importer.data = asset.read_bytes()

        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(self.importer.check_conformity())

        # Missing package.yaml file
        asset = self.assets / "missing_package_yaml.tar"
        self.importer.data = asset.read_bytes()

        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(self.importer.check_conformity())
        for item in cm.output:
            self.assertIn(
                "File `package.yaml` not found.",
                item)

        # Wrong package.yaml file
        asset = self.assets / "wrong_package_yaml.tar"
        self.importer.data = asset.read_bytes()

        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(self.importer.check_conformity())

        # Unknown/not installed module
        asset = self.assets / "wrong_module.tar"
        self.importer.data = asset.read_bytes()

        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(self.importer.check_conformity())
        for item in cm.output:
            self.assertIn(
                "Module not installed: pharmaship.wronginventory",
                item)

        # All good
        asset = self.assets / "good_tar.tar"
        self.importer.data = asset.read_bytes()
        self.assertTrue(self.importer.check_conformity())
