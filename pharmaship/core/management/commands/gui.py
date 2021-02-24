#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Django Command to launch the Pharmaship graphical user interface."""
import os
import django
from pathlib import Path
from django.core.management.base import BaseCommand


def main():  # noqa: D103
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmaship.app.settings')

    from django.core.management import call_command

    # Need to setup Django first to register our Apps
    django.setup()

    from django.contrib.contenttypes.models import ContentType
    from django.db.utils import OperationalError
    # Check if first run
    try:
        ContentType.objects.all().count()
    except OperationalError:
        call_command("migrate")
        call_command("populate")

    # Launch the Pharmaship GUI
    call_command("gui")


class Command(BaseCommand):
    """Graphical user interface for Pharmaship."""

    help = "Graphical user interface for Pharmaship."

    def handle(self, *args, **options):  # noqa: D102
        os.environ.setdefault(
            'FONTCONFIG_PATH', str(Path('etc/fonts').resolve())
            )

        from pharmaship.gui.view import Application
        app = Application()
        app.gtk_style()

        app.run(args)
