#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Django Command to populate the database the first time."""
import os

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

from pharmaship.core.utils import log


def load_data(filename):
    """Call loaddata command for loading initial data."""
    path = settings.PHARMASHIP_DATA / filename
    log.debug(path)
    call_command("loaddata", path)


class Command(BaseCommand):
    """Populate the Database for the first launch of Pharmaship."""

    help = "Populate the Database for the first launch of Pharmaship."

    def handle(self, *args, **options):  # noqa: D102
        try:
            settings.PHARMASHIP_CONF.touch()
            log.info("Copy default configuration")
            default_config = settings.PHARMASHIP_DATA / "config_default.yaml"
            data = default_config.read_text()
            settings.PHARMASHIP_CONF.write_text(data)
        except FileExistsError:
            pass

        log.info("Load Equipment Groups")
        load_data("EquipmentGroup.yaml")
        log.info("Load Molecule Groups")
        load_data("MoleculeGroup.yaml")
        log.info("Load default Locations")
        load_data("Location.yaml")
        log.info("Load default Allowance")
        load_data("Allowance.yaml")

        log.info("Load Pharmaship public key")
        key_path = settings.PHARMASHIP_DATA / "pharmaship.pub"
        log.debug(key_path)
        call_command("key_management", "add", key_path)
