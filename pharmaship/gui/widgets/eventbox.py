# -*- coding: utf-8 -*-
"""Customized EventBox widget."""
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk, Gdk


def widget_clicked(source, event, ref_item, cb_func, row_num, data=None):
    """Handle left-click on EventBox."""
    if event.type == Gdk.EventType.BUTTON_PRESS:
        if event.button == 1:
            grid = source.get_parent()
            if data:
                return cb_func(source, grid, ref_item, row_num, data)

            return cb_func(source, grid, ref_item, row_num)


def change_cursor(source, event, width=1):
    """Change cursor to hand-click on entering the widget area."""
    grid = source.get_parent()
    row = grid.child_get_property(source, "top-attach")

    if event.type == Gdk.EventType.ENTER_NOTIFY:
        cursor = Gdk.Cursor.new(Gdk.CursorType.HAND2)
        source.get_root_window().set_cursor(cursor)
        # Add a new class for the whole row (like a CSS hover)
        for i in range(width):
            widget = grid.get_child_at(i, row)
            widget.get_style_context().add_class("clickable-row")
    else:
        for i in range(width):
            widget = grid.get_child_at(i, row)
            widget.get_style_context().remove_class("clickable-row")


def EventBox(ref_item, cb_func, grid_width, row_num, data=None):
    """Create and EventBox with events preconfigured."""
    evbox = Gtk.EventBox()
    evbox.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
    evbox.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
    evbox.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK)
    evbox.connect(
        'button-press-event',
        widget_clicked, ref_item, cb_func, row_num, data
        )
    evbox.connect('enter-notify-event', change_cursor, grid_width)
    evbox.connect('leave-notify-event', change_cursor, grid_width)
    return evbox
