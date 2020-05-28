# -*- coding: utf-8; -*-
"""Test suite for `core` subpackage."""
from django.test import TestCase
from django.conf import settings

from pathlib import Path
from munch import Munch

from pharmaship.core import config
from pharmaship.core.utils import log


class ConfigTestCase(TestCase):
    """Tests for `core.config` methods."""

    def setUp(self):  # noqa: D102
        self.assets = Path(settings.BASE_DIR) / "tests/core/assets"
        self.validator_path = settings.VALIDATOR_PATH
        settings.VALIDATOR_PATH = self.assets

        self.config_file = settings.PHARMASHIP_CONF
        settings.PHARMASHIP_CONF = "dummy"

    def test_load_config(self):
        """Check configuration file loading and parsing."""
        # Invalid YAML
        content = "inval:\nid{yaml},"
        schema = "dummy_schema"
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(config.load_config(content, schema))
        for item in cm.output:
            self.assertIn("Unable to parse the config file.", item)

        # Invalid schema filename
        content = "dummy_content"
        schema = "dummy_schema"
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(config.load_config(content, schema))
        for item in cm.output:
            self.assertIn("Unable to read the schema file.", item)

        # Invalid schema content
        content = "dummy_content"
        schema = Path("config_bad.json")
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(config.load_config(content, schema))
        for item in cm.output:
            self.assertIn("Unable to parse the schema file.", item)

        # Invalid configuration object
        settings.VALIDATOR_PATH = self.validator_path

        schema = "config.json"

        filename = self.assets / "config_bad.yaml"
        try:
            with open(filename, "r") as fdesc:
                content = fdesc.read()
        except IOError as error:
            log.exception("Config file not readable: %s. %s", filename, error)
            return False

        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(config.load_config(content, schema))
        for item in cm.output:
            self.assertIn("Configuration file not validated.", item)

        # All good
        filename = settings.PHARMASHIP_DATA / "config_default.yaml"
        try:
            with open(filename, "r") as fdesc:
                content = fdesc.read()
        except IOError as error:
            log.exception("Config file not readable: %s. %s", filename, error)
            return False

        result = config.load_config(content, schema)
        self.assertIsInstance(result, dict)

    def test_read_config(self):
        """Check configuration file reading from settings."""
        settings.VALIDATOR_PATH = self.validator_path

        # Invalid filename
        settings.PHARMASHIP_CONF = "dummy"
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(config.read_config())
        for item in cm.output:
            self.assertIn("Config file not readable:", item)

        # Invalid config
        settings.PHARMASHIP_CONF = self.assets / "config_bad.yaml"
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(config.read_config())
        for item in cm.output:
            self.assertIn("Configuration file not validated.", item)

        # All good
        settings.PHARMASHIP_CONF = settings.PHARMASHIP_DATA / "config_default.yaml"
        self.assertIsInstance(config.read_config(), Munch)

    def test_write_config(self):
        """Check configuration file writing."""
        # Invalid data
        data = "This is a string, not a Munch instance!"
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(config.write_config(data))
        for item in cm.output:
            self.assertIn("Data is not a Munch instance: 'str' object has no attribute 'toDict'", item)

        # Invalid filename
        settings.VALIDATOR_PATH = self.validator_path
        settings.PHARMASHIP_CONF = settings.PHARMASHIP_DATA / "config_default.yaml"
        data = config.read_config()
        data.vessel.name = "Dummy"

        settings.PHARMASHIP_CONF = self.assets / "config_ro.yaml"
        # Force it read-only to get write failure
        settings.PHARMASHIP_CONF.chmod(0o444)
        with self.assertLogs(log, level='ERROR') as cm:
            self.assertFalse(config.write_config(data))
        for item in cm.output:
            self.assertIn("Config file not writable:", item)
