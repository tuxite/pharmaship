#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand


from core.utils import log

import inventory.models


class Command(BaseCommand):
    help = "Command to add an item."

    def add_arguments(self, parser) -> None:
        subparsers = parser.add_subparsers(help='Action on inventory.')

        parser_allowance = subparsers.add_parser('allowance', help='Add an Allowance instance.')
        parser_allowance.add_argument("--list", action="store_true", help="List the available allowances instances.")
        parser_allowance.set_defaults(func=self.allowance)

        parser_molecule = subparsers.add_parser('molecule', help='Add a Molecule in selected Allowance instance.')
        parser_molecule.add_argument("--list", action="store_true", help="List the available molecule instances.")
        parser_molecule.set_defaults(func=self.molecule)

        parser_equipment = subparsers.add_parser('equipment', help='Add a Equipment in selected Allowance instance.')
        parser_equipment.add_argument("--list", action="store_true", help="List the available equipment instances.")
        parser_equipment.set_defaults(func=self.equipment)



    def handle(self, *args, **options):
        if "func" in options:
            options['func'](options)

    def allowance(self, args):
        log.info("Allowance")
        if "list" in args:
            for item in inventory.models.Allowance.objects.all():
                print(item.pk, item.name)
            return

    def molecule(self, args):
        log.info("Molecule")
        if "list" in args:
            for item in inventory.models.Molecule.objects.all():
                print(item.pk, item)
            return

    def equipment(self, args):
        log.info("Equipment")
        if "list" in args:
            for item in inventory.models.Equipment.objects.all():
                print(item.pk, item)
            return
