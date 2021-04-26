# -*- coding: utf-8 -*-
"""Customized Gtk.Button widget."""
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk, Gio

from pharmaship.gui.utils import get_icon


def ButtonWithImage(
        image_name,
        btn_class=None,
        tooltip=None,
        action=None,
        connect=None,
        data=None
        ):
    """Return a Gtk.Button with a custom image and custom action."""
    if btn_class:
        button = btn_class()
    else:
        button = Gtk.Button()

    if tooltip and isinstance(tooltip, str):
        button.set_tooltip_text(tooltip)

    # icon = Gio.ThemedIcon(name=image_name)
    # image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
    image = get_icon(image_name)
    button.add(image)
    if action and isinstance(action, str):
        button.set_action_name(action)

    if connect:
        button.connect("clicked", connect, data)
    return button
