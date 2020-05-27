#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Django Command to export Pharmaship data manually."""
import argparse
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from pharmaship.core.utils import log

from pharmaship.inventory import models
from pharmaship.inventory.export import create_archive


class Command(BaseCommand):
    """Package export in Pharmaship."""

    help = "Package export in Pharmaship."

    def add_arguments(self, parser) -> None:  # noqa: D102
        subparsers = parser.add_subparsers(help='Export actions.')

        parser_inventory = subparsers.add_parser('inventory', help='Export present inventory.')
        parser_inventory.set_defaults(func=self.inventory)
        parser_inventory.add_argument("filename", help='Output filename')

        parser_allowance = subparsers.add_parser('allowance', help='Export an allowance.')

        sp_allowance = parser_allowance.add_subparsers()

        all_allowances = sp_allowance.add_parser('all', help="Export all allowances.")
        all_allowances.set_defaults(func=self.export_all_allowances)

        single_allowance = sp_allowance.add_parser('id', help="Export one allowance.")
        single_allowance.set_defaults(func=self.allowance)

        single_allowance.add_argument("id", type=int, help="ID of the allowance to export. Can be found with export list command.")
        single_allowance.add_argument("filename", help='Output filename', type=argparse.FileType('wb'))

        parser_list = subparsers.add_parser('list', help='List allowances in database.')
        parser_list.set_defaults(func=self.list_allowance)

    def handle(self, *args, **options):  # noqa: D102
        log.info(args)
        if "func" in options:
            options['func'](options)

    def inventory(self, args):
        log.debug("Inventory export")

    def allowance(self, args):
        """Export selected `Allowance` instance in a tar file."""
        log.debug("Allowance export")

        try:
            allowance = models.Allowance.objects.get(id=args["id"])
        except models.Allowance.DoesNotExist:
            log.error("Allowance does not exists.")
            exit()

        create_archive(allowance, args["filename"])

    def list_allowance(self, args):
        """List `Allowance` objects in database."""
        log.info("Allowances in database:")
        log.info("[ID]  NAME (VERSION)")
        for item in models.Allowance.objects.all().order_by("id"):
            log.info("[{0:02d}]  {1} ({2})".format(item.id, item.name, item.version))

    def export_all_allowances(self, args):
        for item in models.Allowance.objects.exclude(id=0).order_by("id"):
            archive_name = slugify("allowance_{0}_{1}".format(item.name,  item.version))

            self.allowance({"id": item.id, "filename": Path(archive_name).with_suffix(".tar").open('wb')})
