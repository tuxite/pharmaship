# -*- coding: utf-8; -*-
"""Test suite for `gpg` subpackage."""
from django.test import TestCase
from django.conf import settings

from pathlib import Path

from pharmaship.core import gpg


def remove_keyring(path):
    """Remove the specially created keyring if any."""
    settings.KEYRING_PATH.unlink()
    pass


class GPGTestCase(TestCase):
    """Tests for `core.gpg` methods."""

    def setUp(self):  # noqa: D102
        # Create a temporary GPG keyring
        path = ""
        self.addCleanup(remove_keyring, path)

        settings.KEYRING_PATH = Path(settings.BASE_DIR) / "tests/core/keyring"
        self.cls = gpg.KeyManager()

        self.assets = Path(settings.BASE_DIR) / "tests/core/assets"

    def test_add_key(self):
        """Check the GPG is added."""

        pass
