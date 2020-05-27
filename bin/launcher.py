#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Launch Pharmaship GUI from package entry-point."""
import os
import django


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmaship.app.settings')
    from django.core.management import call_command

    # Need to setup Django first to register our Apps
    django.setup()

    # Launch the Pharmaship GUI
    call_command("gui")


if __name__ == '__main__':
    main()
