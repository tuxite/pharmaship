# -*- coding: utf-8 -*-
"""Utilities for Pharmaship GUI."""
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk, GObject, GdkPixbuf

import os.path
import platform
import subprocess

from pluralizer import Pluralizer

from django.utils.translation import gettext as _
from django.conf import settings

from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

from pharmaship.core.utils import log
from pharmaship.inventory import constants


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


def grid_row_class(grid, row_num, width, add=True):
    """Change the class of a row in the grod."""
    if add:
        for i in range(width):
            widget = grid.get_child_at(i, row_num)
            widget.get_style_context().add_class("active-row")
    else:
        for i in range(width):
            widget = grid.get_child_at(i, row_num)
            widget.get_style_context().remove_class("active-row")


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


def item_quantity_changed(source, builder):
    pluralizer = Pluralizer()

    quantity = source.get_value()

    result = source.get_adjustment().get_upper() - quantity
    if result < 0:
        return False

    remaining = builder.get_object("remaining")
    remaining.set_value(result)

    # Adapt plural forms of labels
    consumed_label = builder.get_object("consumed_packing")
    consumed_label.set_text(pluralizer.pluralize(
        consumed_label.get_text(),
        source.get_value()
        ))

    remaining_label = builder.get_object("remaining_packing")
    remaining_label.set_text(pluralizer.pluralize(
        remaining_label.get_text(),
        result
        ))

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


def get_combo_value(combo):
    """Return active value in a Gtk.ComboBox."""
    value = None
    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
        model = combo.get_model()
        value = model[tree_iter][0]

    return value


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


def first_lower(s):
    """Lower the first letter of a string."""
    if not s:  # Added to handle case where s == None
        return
    else:
        return s[0].lower() + s[1:]


def packing_combo(combo, default=None, active=0, num=1):
    pluralizer = Pluralizer()
    # Packing name combox box setup
    store = Gtk.ListStore(int, str)

    active_index = 0

    if default:
        text = pluralizer.pluralize(first_lower(default), num)
        store.append([0, text])

    index = 1
    for item in constants.PACKING_CHOICES[1:]:
        text = pluralizer.pluralize(str(item[1]), num)
        store.append([item[0], text])

        if active and item[0] == active:
            active_index = index

        index += 1

    combo.set_model(store)
    renderer_text = Gtk.CellRendererText()
    combo.clear()
    combo.pack_start(renderer_text, True)
    combo.add_attribute(renderer_text, "text", 1)
    combo.set_active(active_index)


def toggle_packing(source, builder):
    active = get_combo_value(source)

    items = ["packing_of-label", "packing_form", "packing_content"]

    if active == 0:
        for item in items:
            builder.get_object(item).hide()
    elif active >= 20:
        # Show/hide elements
        for item in items[:-1]:
            builder.get_object(item).show()
        builder.get_object(items[-1]).hide()
        # Adapt plural form
        builder.get_object("packing_content").set_value(int(active/10))
    else:
        for item in items:
            builder.get_object(item).show()


def update_packing_form(source, builder):
    pluralizer = Pluralizer()
    obj = builder.get_object("packing_form")
    plural = pluralizer.pluralize(
        obj.get_text(),
        source.get_value()
        )

    obj.set_text(plural)


def update_packing_combo(source, builder, default):
    num = source.get_value()
    combo = builder.get_object("packing_combo")
    active = get_combo_value(combo)
    packing_combo(combo, default, active, num)
