#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Launch Pharmaship GUI from package entry-point."""
import os
import django


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmaship.app.settings')

    # Need to setup Django first to register our Apps
    django.setup()

    from django.core.management import call_command

    # Check if first run
    from django.contrib.contenttypes.models import ContentType
    from django.db.utils import OperationalError
    try:
        ContentType.objects.all().count()
    except OperationalError:
        call_command("migrate")
        call_command("populate")

    # Launch the Pharmaship GUI
    call_command("gui")


if __name__ == '__main__':
    main()
