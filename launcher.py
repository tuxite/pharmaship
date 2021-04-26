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

from pharmaship.app import settings


GRESOURCE_PATH = settings.PHARMASHIP_GUI / "resources.gresource"


def splash_screen():
    """Display a splash screen during Django initialization."""
    resource = Gio.resource_load(str(GRESOURCE_PATH))
    Gio.Resource._register(resource)

    builder = Gtk.Builder.new_from_resource("/com/devmaretique/pharmaship/ui/splash_screen.ui")
    builder.set_translation_domain("com.devmaretique.pharmaship")

    window = builder.get_object("window")
    window.show_all()

    label = builder.get_object("status")

    return window, label


def main():  # noqa: D103
    window, label = splash_screen()

    def update_label(text):
        label.set_text(text)

    def cleanup(main_window):
        Gtk.main_quit()
        window.destroy()
        main_window.run()
        t.join()

    def thread_run():
        # Call the class method to generate a temporary PDF file
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmaship.app.settings')

        # Need to setup Django first to register our Apps
        django.setup()

        GLib.idle_add(update_label, "Django setup done")
        from django.core.management import call_command

        # Check if first run
        from django.contrib.contenttypes.models import ContentType
        from django.db.utils import OperationalError
        try:
            ContentType.objects.all().count()
        except OperationalError:
            GLib.idle_add(update_label, "Database initialization in progress")
            call_command("migrate")
            call_command("populate")

        GLib.idle_add(update_label, "Django initialized")
        # Launch the Pharmaship GUI
        from pharmaship.gui.view import Application
        app = Application()
        app.gtk_style()

        GLib.idle_add(update_label, "All done! Wait for magic :)")
        GLib.idle_add(cleanup, app)

    t = threading.Thread(target=thread_run)
    t.start()

    Gtk.main()


if __name__ == '__main__':
    main()
