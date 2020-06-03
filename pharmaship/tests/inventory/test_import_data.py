# -*- coding: utf-8; -*-
"""Test suite for `import_data` subpackage."""
import tarfile

from pathlib import Path

from django.test import TestCase
from django.conf import settings


class ImportMethodTestCase(TestCase):
    """Tests for `inventory.import_data` methods."""

    def setUp(self):  # noqa: D102
        self.assets = Path(settings.BASE_DIR) / "tests/inventory/assets"

    def test_picture_files(self):
        pass
