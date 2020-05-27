#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Command to import Pharmaship packages."""
import argparse

from django.core.management.base import BaseCommand

from pharmaship.core.import_data import Importer
from pharmaship.core.utils import log


class Command(BaseCommand):
    """Package import in Pharmaship."""

    help = "Package import in Pharmaship."

    def add_arguments(self, parser) -> None:  # noqa: D102
        parser.add_argument(
            "file",
            help='Package filename.',
            type=argparse.FileType('r')
            )

    def handle(self, *args, **options):  # noqa: D102
        handler = Importer()

        if not handler.read_package(options["file"]):
            exit(handler.status)

        if not handler.check_signature():
            exit(handler.status)

        if not handler.check_conformity():
            exit(handler.status)

        handler.deploy()
