# -*- coding: utf-8 -*-
"""Customized Gtk.Button widget."""
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk

import datetime
import re

from django.utils.translation import gettext as _


class EntryMasked(Gtk.Entry, Gtk.Editable):
    """Gtk.Entry with text mask implementation."""

    def __init__(self, mask, activate_cb=None):
        super().__init__()
        self.mask = mask
        self.mask_text = mask["format"]
        self.mask_length = len(mask["format"])

        if "allowed_chars" not in mask:
            self.allowed = None
        else:
            self.allowed = mask["allowed_chars"]

        # Activate callback (as this parameter is not accessible from the
        # parent object.
        if activate_cb:
            if isinstance(activate_cb, tuple):
                self.connect("activate", *activate_cb)
            else:
                self.connect("activate", activate_cb)

    def add_one_more(self, text, length, character):
        if (length + 1) > self.mask_length:
            return text

        if self.mask_text[length] == "_":
            return text + character

        text += self.mask_text[length]
        return self.add_one_more(text, length + 1, character)

    def do_insert_text(self, new_text, length, position):

        previous_text = self.get_text()
        previous_length = len(previous_text)

        added_text = ""
        for i in range(length):
            if self.allowed and new_text[i] not in self.allowed:
                continue

            if (previous_length + i + 1) > self.mask_length:
                return position

            added_text += self.add_one_more(added_text, previous_length + i, new_text[i])

        # Final modification
        self.get_buffer().insert_text(position, added_text, len(added_text))

        # Check regex and change style if invalid
        self.set_icon_from_icon_name(1, None)
        self.set_icon_tooltip_markup(1, None)
        self.get_style_context().remove_class("error")
        # if len(previous_text + added_text) == self.mask_length:
        if len(self.get_text()) == self.mask_length:
            if not self.check_value(previous_text + added_text):
                self.get_style_context().add_class("error")
                self.set_icon_from_icon_name(1, "error")
                self.set_icon_tooltip_markup(1, _("Invalid date input"))
        return position + len(added_text)

    def check_value(self, text):
        if "regex" in self.mask and self.mask["regex"] is not None:
            return re.match(self.mask["regex"], text)

        if "datetime" in self.mask and self.mask["datetime"] is not None:
            try:
                datetime.datetime.strptime(text, self.mask["datetime"])
            except ValueError:
                return False

        # Nothing special...
        return True
