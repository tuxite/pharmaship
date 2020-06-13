# -*- coding: utf-8 -*-
"""Utilities for Pharmaship GUI."""
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk, Gio, GObject, GdkPixbuf

import os.path
import re
import datetime
import platform
import subprocess

from django.utils.translation import gettext as _
from django.conf import settings

from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

from pharmaship.core.utils import log


def get_template(filename):
    """Return GUI file path."""
    return os.path.join(settings.PHARMASHIP_GUI, filename)


def grid_replace(old_widget, new_widget):
    # Get parent (the grid)
    parent = old_widget.get_parent()
    position = {
        "left-attach": None,
        "top-attach": None,
        "width": None,
        "height": None
    }
    # Store old_widget position
    for key in position:
        position[key] = parent.child_get_property(old_widget, key)
    old_widget.destroy()

    # Apply the stored position to the new widget
    parent.add(new_widget)
    for key in position:
        parent.child_set_property(new_widget, key, position[key])

    new_widget.show_all()
    return new_widget


def error_field_changed(source):
    if isinstance(source, Gtk.Entry):
        source.set_icon_from_icon_name(1, None)
        source.set_icon_tooltip_markup(1, None)
        source.get_style_context().remove_class("error")

    if isinstance(source, Gtk.ComboBox):
        source.get_style_context().remove_class("error-combobox")

    if isinstance(source, Gtk.TextView):
        source.get_style_context().remove_class("error-textview")

    # Remove this signal
    disconnect_signal(source, "changed")


def set_errors(form, builder, fields):
    log.error("Form is not valid")
    log.debug(form.errors.as_json())
    for item in form.errors:
        if "_id" in item:
            item = item.split("_id")[0]
        # Get the widget
        if ("entry" in fields and item in fields["entry"]) or \
           ("spinbutton" in fields and item in fields["spinbutton"]):
            entry = builder.get_object(item)
            entry.get_style_context().add_class("error")
            entry.set_icon_from_icon_name(1, "error")

            item_errors = "\n".join(form.errors[item])
            entry.set_icon_tooltip_markup(1, item_errors)

            entry.connect("changed", error_field_changed)

        if "combobox" in fields and item in fields["combobox"]:
            combobox = builder.get_object(item)
            combobox.get_style_context().add_class("error-combobox")
            combobox.connect("changed", error_field_changed)

        if "textview" in fields and item in fields["textview"]:
            textview = builder.get_object(item + "_buffer")
            textview.get_style_context().add_class("error-textview")
            textview.connect("changed", error_field_changed)
    return


def get_form_data(form_class, builder, fields, data={}):
    if "entry" in fields:
        for item in fields["entry"]:
            widget = builder.get_object(item)
            data[item] = widget.get_text()

    if "spinbutton" in fields:
        for item in fields["spinbutton"]:
            widget = builder.get_object(item)
            data[item] = widget.get_value()

    if "combobox" in fields:
        for item in fields["combobox"]:
            data[item + "_id"] = None
            widget = builder.get_object(item)
            tree_iter = widget.get_active_iter()
            if tree_iter is not None:
                model = widget.get_model()
                data[item + "_id"] = model[tree_iter][0]

    if "textview" in fields:
        for item in fields["textview"]:
            buffer = builder.get_object(item + "_buffer")
            start = buffer.get_start_iter()
            end = buffer.get_end_iter()
            data[item] = buffer.get_text(start, end, False)

    if "switch" in fields:
        for item in fields["switch"]:
            switch = builder.get_object(item)
            data[item] = switch.get_active()

    form = form_class(data)

    if not form.is_valid():
        set_errors(form, builder, fields)
        return None

    return form.cleaned_data


def dialog_destroy(source, dialog):
    """Destroy a Gtk.Dialog widget.

    `source`: event source widget. Not used.
    `dialog`: Gtk.Dialog widget to delete.
    """
    dialog.destroy()


def item_quantity_changed(source, remaining):
    quantity = source.get_value()

    result = source.get_adjustment().get_upper() - quantity
    if result < 0:
        return False
    remaining.set_value(result)

    return True


def location_combo(combo, locations, active=None, empty=None, exclude=None):
    # Location combox box setup
    store = Gtk.ListStore(int, str)

    index = 0

    active_index = -1
    if empty:
        store.append([None, ""])
        index += 1

    for item in locations:
        if len(item["sequence"]) > 1:
            location_str = " > ".join(item["sequence"])
        else:
            location_str = item["sequence"][0]

        # Do not allow the selection of excluded id (ie: self referencing)
        if exclude and item["id"] in exclude:
            continue

        if item["rescue_bag"]:
            location_str = "<span foreground=\"royalblue\" weight=\"bold\">{0}</span>".format(location_str)
        elif item["id"] < 100:
            location_str = "<span foreground=\"darkorange\" weight=\"bold\">{0}</span>".format(location_str)

        store.append([item["id"], location_str])

        if active and item["id"] == active:
            active_index = index

        index += 1

    combo.set_model(store)
    renderer_text = Gtk.CellRendererText()
    combo.pack_start(renderer_text, True)
    combo.add_attribute(renderer_text, "markup", 1)
    combo.set_active(active_index)


def reason_combo(combo, expired=False):
    # Location combox box setup
    store = Gtk.ListStore(int, str)

    store.append([4, _("Perished")])
    store.append([9, _("Other")])

    combo.set_model(store)
    renderer_text = Gtk.CellRendererText()
    combo.pack_start(renderer_text, True)
    combo.add_attribute(renderer_text, "text", 1)

    # To ease the user experience, select the most probable reason
    if expired:
        combo.set_active(0)
    else:
        combo.set_active(1)

def get_reason(reason_combo):
    reason = None
    tree_iter = reason_combo.get_active_iter()
    if tree_iter is not None:
        model = reason_combo.get_model()
        reason = model[tree_iter][0]

    return reason


def picture_frame(source, picture):
    """Display a window with a picture.

    The window is destroyed when loosing the focus.
    """
    # Create the widget
    picture_window = Gtk.Window(title=_("Picture"))
    picture_window.set_transient_for(source.get_toplevel())
    picture_window.set_modal(False)
    picture_window.set_default_size(800, 600)

    picture_window.connect("focus-out-event", picture_window_destroy)

    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=str(settings.PICTURES_FOLDER / picture.name),
        width=800,
        height=600,
        preserve_aspect_ratio=True
        )
    # pixbuf = pixbuf.scale_simple(600, 600, GdkPixbuf.InterpType.BILINEAR)
    picture_widget = Gtk.Image.new_from_pixbuf(pixbuf)
    picture_window.add(picture_widget)

    picture_window.show_all()


def picture_window_destroy(source, event):
    source.destroy()


def export_pdf(pdf_filename, html_string, css_string):
    font_config = FontConfiguration()
    html = HTML(string=html_string)
    css = CSS(string=css_string, font_config=font_config)
    html.write_pdf(
        target=pdf_filename,
        stylesheets=[css],
        font_config=font_config)


def open_file(filename):
    # Open the pdf file using the platform default program
    if filename:
        if platform.system() == 'Darwin':
            subprocess.call(('open', filename))
        elif platform.system() == 'Windows':
            os.startfile(filename)
        else:
            subprocess.call(('xdg-open', filename))


def disconnect_signal(source, signal):
    signal_id = GObject.signal_lookup(signal, source.__class__)
    handler_id = GObject.signal_handler_find(source, GObject.SignalMatchType.ID, signal_id, 0, None, 0, 0)
    source.disconnect(handler_id)


def set_focus(source, event, row_num):
    viewport = source.get_children()[0]
    grid = viewport.get_children()[0]
    vadjust = viewport.get_vadjustment()
    # Get the corresponding widget
    widget = grid.get_child_at(0, row_num)
    widget.set_can_focus(True)
    widget.grab_focus()
    # Put this widget on top of the view
    vadjust.set_value(widget.get_allocation().y)

    # Disconnect this signal otherwise the view is unusable
    disconnect_signal(source, "draw")


def ButtonWithImage(image_name, btn_class=None, tooltip=None, action=None, connect=None, data=None):
    if btn_class:
        button = btn_class()
    else:
        button = Gtk.Button()

    if tooltip and isinstance(tooltip, str):
        button.set_tooltip_text(tooltip)

    icon = Gio.ThemedIcon(name=image_name)
    image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
    button.add(image)
    if action and isinstance(action, str):
        button.set_action_name(action)

    if connect:
        button.connect("clicked", connect, data)
    return button


# Custom Gtk widgets
# class ListBoxRowWithData(Gtk.ListBoxRow):
#     def __init__(self, data):
#         super(Gtk.ListBoxRow, self).__init__()
#         self.data = data
#         self.show = False


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
