# -*- coding: utf-8; -*-
"""Test suite for `gpg` subpackage."""
from django.test import TestCase
from django.conf import settings

from pathlib import Path

from pharmaship.core.utils import log

from pharmaship.core import gpg


def remove_keyring(path):
    """Remove the specially created keyring if any."""
    for item in path.iterdir():
        if item.is_dir():
            remove_keyring(item)
        else:
            item.unlink(missing_ok=True)
    path.rmdir()


class GPGTestCase(TestCase):
    """Tests for `core.gpg` methods."""

    def setUp(self):  # noqa: D102
        # Create a temporary GPG keyring
        path = Path(settings.BASE_DIR) / "tests/core/keyring"
        self.addCleanup(remove_keyring, path)

        settings.KEYRING_PATH = path
        path.mkdir(parents=True, exist_ok=True)
        self.km = gpg.KeyManager()

        self.assets = Path(settings.BASE_DIR) / "tests/core/assets"

    def test_add_key(self):
        """Check the GPG key is added."""
        # Bad key
        key = self.assets / "bad_key.pub"
        key_obj = key.open()

        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(self.km.add_key(key_obj))
        for item in cm.output:
            self.assertIn("Signature error:", item)

        # Good key (first)
        key = settings.PHARMASHIP_DATA / "pharmaship.pub"
        key_obj = key.open()

        output = {
            'name': 'Pharmaship 2020 <pharmaship@devmaretique.com>',
            'fingerprint': '86A7CC93CA482E093C28E5C236A33034D31E80F6'
            }

        with self.assertLogs(log, level='DEBUG') as cm:
            self.assertTrue(self.km.add_key(key_obj))
        for item in cm.output:
            self.assertIn(str(output), item)

        # Good key (already imported)
        key_obj = key.open()
        with self.assertLogs(log, level='INFO') as cm:
            self.assertTrue(self.km.add_key(key_obj))
        for item in cm.output:
            self.assertIn("Key already added.", item)

    def test_key_list(self):
        """Check the keyring list."""
        # Empty keyring
        self.assertEqual(self.km.key_list(), [])

        # Add Pharmaship Key
        key = settings.PHARMASHIP_DATA / "pharmaship.pub"
        key_obj = key.open()
        with self.assertLogs(log, level='DEBUG'):
            self.km.add_key(key_obj)

        output = [{
            'name': 'Pharmaship 2020 <pharmaship@devmaretique.com>',
            'fingerprint': '86A7CC93CA482E093C28E5C236A33034D31E80F6'
            }]

        self.assertEqual(self.km.key_list(), output)

    def test_get_key(self):
        """Check the key retrival."""
        # Add Pharmaship Key
        key = settings.PHARMASHIP_DATA / "pharmaship.pub"
        key_obj = key.open()
        with self.assertLogs(log, level='DEBUG'):
            self.km.add_key(key_obj)

        fingerprint = "86A7CC93CA482E093C28E5C236A33034D31E80F6"
        self.assertIsNotNone(self.km.get_key(fingerprint))

        # Wrong fingerprint
        fingerprint = "96A7CC93CA482E093C28E5C236A33034D31E80F6"
        self.assertIsNone(self.km.get_key(fingerprint))

    def test_delete_key(self):
        """Check key deletion."""
        # Add Pharmaship Key
        key = settings.PHARMASHIP_DATA / "pharmaship.pub"
        key_obj = key.open()
        with self.assertLogs(log, level='DEBUG') as cm:
            self.km.add_key(key_obj)

        # Wrong fingerprint
        fingerprint = "96A7CC93CA482E093C28E5C236A33034D31E80F6"
        with self.assertLogs(log, level='ERROR') as cm:
            self.km.delete_key(fingerprint)
        for item in cm.output:
            self.assertIn("Key not found:", item)

        # Good fingerprint
        fingerprint = "86A7CC93CA482E093C28E5C236A33034D31E80F6"
        self.assertTrue(self.km.delete_key(fingerprint))

    def test_check_signature(self):
        """Check signature verification."""

        # Add Pharmaship Key
        key = settings.PHARMASHIP_DATA / "pharmaship.pub"
        key_obj = key.open()
        with self.assertLogs(log, level='DEBUG') as cm:
            self.km.add_key(key_obj)

        # No valid signature
        asset = self.assets / "invalid_signature.tar.asc"
        result = self.km.check_signature(asset.read_text())
        self.assertFalse(result)

        # Key not registered
        asset = self.assets / "unknown_signature.tar.asc"
        result = self.km.check_signature(asset.read_text())
        self.assertFalse(result)

        # All good
        asset = self.assets / "good_signature.tar.asc"
        with self.assertLogs(log, level='INFO') as cm:
            result = self.km.check_signature(asset.read_text())
            self.assertIsNot(result, False)
            self.assertIsInstance(result, bytes)
        for item in cm.output:
            self.assertIn("Package signature correct and verified", item)
