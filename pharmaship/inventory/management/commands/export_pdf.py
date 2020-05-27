#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

from django.core.management.base import BaseCommand


from core.utils import log

import inventory.models
import inventory.medicines.utils

class Command(BaseCommand):
    help = "Export as PDF."

    def add_arguments(self, parser) -> None:
        subparsers = parser.add_subparsers(help='Action on inventory.')

        parser_medicines = subparsers.add_parser('medicines', help='Export medicines inventory.')
        parser_medicines.add_argument("filename", type=argparse.FileType('w'), help="Export filename for pdf")
        parser_medicines.add_argument("--html", action="store_true", help="Export in html.")
        parser_medicines.set_defaults(func=self.medicines)

        # parser_molecule = subparsers.add_parser('molecule', help='Add a Molecule in selected Allowance instance.')
        # parser_molecule.add_argument("--list", action="store_true", help="List the available molecule instances.")
        # parser_molecule.set_defaults(func=self.molecule)
        #
        # parser_equipment = subparsers.add_parser('equipment', help='Add a Equipment in selected Allowance instance.')
        # parser_equipment.add_argument("--list", action="store_true", help="List the available equipment instances.")
        # parser_equipment.set_defaults(func=self.equipment)



    def handle(self, *args, **options):
        if "func" in options:
            options['func'](options)

    def medicines(self, args):
        log.info("Export medicines")

        # Get filename
        if not "filename" in args:
            log.error("No filename provided")
            exit()

        # log.info("Func medicines")
        template_filename = "gui/templates/medicines_report.html"

        html_string = inventory.medicines.utils.export_html(template_filename)

        if "html" in args and args["html"]:
            try:
                with open(args["filename"].name + ".html", "w") as fdesc:
                    fdesc.write(html_string)
            except IOError as error:
                log.error("File not writable: %s", error)

        try:
            with open("gui/templates/report.css", "r") as fdesc:
                css_string = fdesc.read()
        except IOError as error:
            log.error("CSS file not readable: %s", error)
            exit()

        inventory.medicines.utils.export_pdf(
            pdf_filename=args["filename"].name,
            html_string=html_string,
            css_string=css_string
            )
