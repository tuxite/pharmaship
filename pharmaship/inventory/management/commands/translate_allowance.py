#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gettext
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from django.conf import settings

from pharmaship.core.utils import log, get_content_types

from pharmaship.inventory.models import Allowance, Equipment, Molecule
from pharmaship.inventory.export import serialize_allowance, create_pot, create_po


def get_allowance(id):
    """Return the Allowance instance if any, None otherwise."""
    try:
        allowance = Allowance.objects.get(id=id)
    except Allowance.DoesNotExist:
        log.error("Allowance does not exists.")
        return None
    return allowance


def get_po_filename(lang, allowance):
    """Return the PO filename using locale path convention."""
    result = settings.TRANSLATIONS_FOLDER / lang / "LC_MESSAGES" / "{0}.po".format(slugify(allowance.name))
    return result


def get_pot_filename(allowance):
    """Return the POT filename using locale path convention."""
    result = settings.TRANSLATIONS_FOLDER / "{0}.pot".format(slugify(allowance.name))
    return result


class Command(BaseCommand):
    help = "Command to translate an Allowance."

    def add_arguments(self, parser) -> None:  # noqa: D102
        lang_list = [code for code, name in settings.LANGUAGES]
        subparsers = parser.add_subparsers(help='Translate an Allowance.')

        parser_export = subparsers.add_parser(
            'generate',
            help='Generate a PO or POT file from Allowance data.')
        parser_export.add_argument(
            "--po",
            type=str,
            metavar="XX",
            choices=lang_list,
            help="Generate a PO file from database data. Language code in ISO 639-1 format (ie. 'fr')"
        )
        parser_export.add_argument(
            "--pot",
            action='store_true',
            help="Generate a POT file from database data."
        )
        parser_export.add_argument(
            "--filename",
            type=Path,
            help="Language code in ISO 639-1 format (ie. 'fr')"
            )
        parser_export.set_defaults(func=self.generate_po)

        parser_import = subparsers.add_parser(
            'merge',
            help='Merge a PO file with database Allowance data.')
        parser_import.add_argument(
            "--lang",
            type=str,
            choices=lang_list,
            required=True,
            help="Language code in ISO 639-1 format (ie. 'fr')"
            )
        parser_import.add_argument(
            "--filename",
            type=Path,
            default=settings.TRANSLATIONS_FOLDER,
            help="Path to locale directory"
            )
        parser_import.set_defaults(func=self.import_po)

        parser.add_argument(
            "--id",
            type=int,
            required=True,
            help="ID of the concerned Allowance."
            )

    def handle(self, *args, **options):  # noqa: D102
        allowance = get_allowance(options["id"])
        if allowance is None:
            exit()

        if "func" in options:
            options['func'](allowance, options)
        else:
            exit("Nothing to do")

    def generate_po(self, allowance, options):
        if options["po"] and options["pot"] is True:
            exit("You must choose between \"po\" and \"pot\", not both.")

        log.info("Parse allowance")
        content = ""

        if options["pot"]:
            content = create_pot(allowance)
            filename = get_pot_filename(allowance)

        if options["po"]:
            content = create_po(allowance, options["po"])
            filename = get_po_filename(options["po"], allowance)

        if options["filename"]:
            filename = options["filename"]

        log.info("Write to file:")
        log.info(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(content)
        return

    def import_po(self, allowance, options):
        if options["lang"] == "en":
            log.info("English is the default language.")
            exit("Nothing to do")

        lang = options["lang"][0:2].lower()
        # Path must be:
        # <localdir>/<language>/LC_MESSAGES/domain.mo
        if options["filename"].exists() is False:
            log.error("Locale directory does not exist.")
            return False

        domain = slugify(allowance.name)
        full_filename = options["filename"] / options["lang"] / "LC_MESSAGES" / (domain + ".mo")

        if full_filename.exists() is False:
            log.error("Message catalog does not exist:")
            log.error(str(full_filename))
            return False

        trad = gettext.translation(
            domain=domain,
            localedir=options["filename"].resolve(),
            languages=[options["lang"]]
        )

        _ = trad.gettext

        # Parse the allowance
        content_types = get_content_types()
        _data, equipment_list, molecule_list = serialize_allowance(allowance, content_types)
        # Update one by one...
        to_update = []
        for equipment in equipment_list:
            setattr(
                equipment,
                "name_{0}".format(lang),
                _(equipment.name_en)
                )
            setattr(
                equipment,
                "packaging_{0}".format(lang),
                _(equipment.packaging_en)
                )
            setattr(
                equipment,
                "remark_{0}".format(lang),
                _(equipment.remark_en)
                )
            to_update.append(equipment)
        Equipment.objects.bulk_update(
            to_update,
            [
                "name_{0}".format(lang),
                "packaging_{0}".format(lang),
                "remark_{0}".format(lang),
            ])

        to_update = []
        for molecule in molecule_list:
            setattr(
                molecule,
                "name_{0}".format(lang),
                _(molecule.name_en)
                )
            setattr(
                molecule,
                "composition_{0}".format(lang),
                _(molecule.composition_en)
                )
            setattr(
                molecule,
                "remark_{0}".format(lang),
                _(molecule.remark_en)
                )
            to_update.append(molecule)
        Molecule.objects.bulk_update(
            to_update,
            [
                "name_{0}".format(lang),
                "composition_{0}".format(lang),
                "remark_{0}".format(lang),
            ])
        return
