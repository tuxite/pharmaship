# -*- coding: utf-8 -*-
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk

import shutil
import datetime

from pathlib import Path

from django.utils.translation import gettext as _
from django.conf import settings

from pharmaship.core.utils import log

from pharmaship.gui import utils


class DatabaseImport:
    """Class handling SQLite database import with GUI."""
    def __init__(self, window):
        self.window = window
        self.params = window.params

    def show_dialog(self):
        builder = utils.get_builder("dev/db_import.ui")
        dialog = builder.get_object("dialog")

        builder.connect_signals({
            "on-response": (self.db_import, dialog),
            "on-cancel": (utils.dialog_destroy, dialog)
        })

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def db_import(self, source, dialog):
        """Copy database from file to pharmaship database location."""
        filename = dialog.get_filename()
        if not filename:
            return False

        # Create a backup copy
        db_filename = settings.DATABASES['default']['NAME']
        bak_filename = db_filename + ".bak"

        shutil.copy(db_filename, bak_filename)

        # Overwrite the current database by the selected file
        try:
            shutil.copy(filename, db_filename)
        except shutil.SameFileError as error:
            log.warning("Using the same filename, so nothing to do. %s", error)

        self.params.refresh()

        dialog.destroy()
        self.success_dialog()
        return True

    def success_dialog(self):
        """Show a Gtk.MessageDialog to inform the DB copy went fine."""
        builder = utils.get_builder("dev/db_import_dialog.ui")
        dialog = builder.get_object("dialog")

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()


class DatabaseExport:
    """Class handling SQLite database import with GUI."""
    def __init__(self, window):
        self.window = window
        self.params = window.params

    def show_dialog(self):
        builder = utils.get_builder("dev/db_export.ui")
        dialog = builder.get_object("dialog")

        builder.connect_signals({
            "on-response": (self.db_export, dialog),
            "on-cancel": (utils.dialog_destroy, dialog)
        })

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def db_export(self, source, dialog):
        """Copy pharmaship database to user selected path."""
        path = dialog.get_filename()
        if not path:
            return False

        # Create a timestamped filename
        filename = "pharmaship_{0}.db".format(datetime.datetime.now().strftime("%Y-%m-%d_%H%M"))
        db_filename = settings.DATABASES['default']['NAME']

        try:
            shutil.copy(db_filename, (Path(path) / filename))
        except OSError as error:
            log.exception("File impossible to save: %s. %s", filename, error)
            self.error_dialog(error)
            return False

        dialog.destroy()
        self.success_dialog()
        return True

    def success_dialog(self):
        """Show a Gtk.MessageDialog to inform the DB backup went fine."""
        builder = utils.get_builder("dev/db_export_dialog.ui")
        dialog = builder.get_object("dialog")

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def error_dialog(self, error):
        """Show a Gtk.MessageDialog to inform about the error."""
        builder = utils.get_builder("dev/db_export_error.ui")
        dialog = builder.get_object("dialog")
        dialog.props.secondary_text = error

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()
