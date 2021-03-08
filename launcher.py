#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Launch Pharmaship GUI from package entry-point."""
import os
import django
import gi
import threading

from pathlib import Path

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio


def splash_screen():
    """Display a splash screen during Django initialization."""
    template = Path(".") / "lib" / "pharmaship" / "gui" / "templates" / "splash_screen.glade"
    if not template.exists():
        template = Path(".") / "pharmaship" / "gui" / "templates" / "splash_screen.glade"
    builder = Gtk.Builder.new_from_file(str(template))
    builder.set_translation_domain("com.devmaretique.pharmaship")

    window = builder.get_object("window")
    window.show_all()

    return window


def main():  # noqa: D103
    window = splash_screen()

    def thread_run():
        # Call the class method to generate a temporary PDF file
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
        from pharmaship.gui.view import Application
        app = Application()
        app.gtk_style()

        GLib.idle_add(cleanup, window, app)

    def cleanup(splash, mainwindow):
        Gtk.main_quit()
        splash.destroy()
        mainwindow.run()
        t.join()

    t = threading.Thread(target=thread_run)
    t.start()

    Gtk.main()


if __name__ == '__main__':
    main()
