# -*- coding: utf-8 -*-
"""Customized Gtk.Button widget."""
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk

import datetime
import re

from django.utils.translation import gettext as _
from pharmaship.core.utils import end_of_month


class EntryMasked(Gtk.Entry, Gtk.Editable):
    """Gtk.Entry with text mask implementation."""

    def __init__(self, mask, activate_cb=None):
        """Superclass Gtk.Entry and Gtk.Editable classes.

        :param dict mask: Mask information to use for validating input.

        :param object activate_cb: Callback function to connect to the widget.

        """
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

    def do_activate(self):
        """Check content validity on activate event."""
        self.check_validity()
        # Put the cursor at the end of the text
        self.set_position(-1)

    def do_focus_out_event(self, event):
        """Check content validity on focus out event."""
        self.check_validity()

    def do_insert_text(self, new_text, length, position):
        previous_text = self.get_text()
        previous_length = len(previous_text)

        added_text = ""
        for i in range(length):
            if self.allowed and new_text[i] not in self.allowed:
                continue

            if (previous_length + i + 1) > self.mask_length:
                return position

            added_text += self.add_one_more(
                text=added_text,
                length=previous_length + i,
                character=new_text[i]
                )

        # Final modification
        self.get_buffer().insert_text(position, added_text, len(added_text))

        # Check regex and change style if invalid
        self.set_icon_from_icon_name(1, None)
        self.set_icon_tooltip_markup(1, None)
        self.get_style_context().remove_class("error")
        # if len(previous_text + added_text) == self.mask_length:
        if len(self.get_text()) == self.mask_length:
            if not self.check_value(previous_text + added_text):
                self.set_invalid_style()
        return position + len(added_text)

    def add_one_more(self, text, length, character):
        if (length + 1) > self.mask_length:
            return text

        if self.mask_text[length] == "_":
            return text + character

        text += self.mask_text[length]
        return self.add_one_more(text, length + 1, character)

    def set_invalid_style(self):
        self.get_style_context().add_class("error")
        self.set_icon_from_icon_name(1, "error")
        self.set_icon_tooltip_markup(1, _("Invalid date input"))

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

    def check_validity(self):
        """Check content validity and autocomplete if defined in mask."""
        text = self.get_text()
        valid = False

        if len(text) == self.mask_length:
            valid = self.check_value(text)

        # The text is valid, nothing else to do
        if valid:
            return

        # There is nothing to do but the text is invalid anyway or
        # we can do something but there is not enough text
        if "min-length" not in self.mask or \
           len(text) < self.mask["min-length"]:
            return self.set_invalid_style()

        # Start completion
        # if "regex" in self.mask and "default" in self.mask:
        #     # TODO
        #     pass

        if "datetime" in self.mask and "min-datetime" in self.mask:
            text = text.strip("-/.")
            temp_date = datetime.datetime.strptime(text, self.mask["min-datetime"])

            if "default-day" in self.mask and \
               self.mask["default-day"] == "endofmonth":
                temp_date = end_of_month(temp_date)

            new_date = temp_date.strftime(self.mask["datetime"])

            self.get_buffer().set_text(new_date, len(new_date))
