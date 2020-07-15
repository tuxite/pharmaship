# -*- coding: utf-8 -*-
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk

from django.utils.translation import gettext as _

from pharmaship.core.utils import log, query_count_all

from pharmaship.inventory.models import Location
from pharmaship.inventory.forms import LocationForm

from pharmaship.gui import utils, widgets


class View:
    def __init__(self, window):
        self.window = window
        self.builder = window.builder
        self.params = window.params

    def create_main_layout(self):
        # Create content
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.props.hscrollbar_policy = Gtk.PolicyType.NEVER
        # No overlay of the scrollbar
        self.scrolled.props.overlay_scrolling = False
        self.window.layout.pack_start(self.scrolled, True, True, 0)

        self.build_grid()
        self.build_action_bar()

        self.window.layout.show_all()

    def build_action_bar(self):
        action_bar = Gtk.ActionBar()
        add_btn = Gtk.Button(_("New Location"))
        add_btn.connect("clicked", self.dialog_add)
        add_btn.get_style_context().add_class("location-btn-add")
        action_bar.pack_start(add_btn)

        self.window.layout.pack_end(action_bar, False, False, 0)

    def location_row_buttons(self, item, row_index):
        linked_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        linked_btn.get_style_context().add_class("linked")
        linked_btn.get_style_context().add_class("medicine-item-buttons")

        # Modify
        btn_modify = widgets.ButtonWithImage("document-edit-symbolic", tooltip="Modify", connect=self.dialog_modify, data=item)
        linked_btn.pack_end(btn_modify, False, True, 0)
        # Delete
        if item["id"] > 100:
            btn_delete = widgets.ButtonWithImage("edit-delete-symbolic", tooltip="Delete", connect=self.dialog_delete, data=item)
            btn_delete.get_style_context().add_class("medicine-btn-delete")
            linked_btn.pack_end(btn_delete, False, True, 0)

        self.grid.attach(linked_btn, 1, row_index, 1, 1)

    def build_grid(self):

        self.grid = Gtk.Grid()
        self.scrolled.add(self.grid)

        # Header
        label = Gtk.Label(_("Location"), xalign=0)
        label.set_hexpand(True)
        label.get_style_context().add_class("header-cell")
        self.grid.attach(label, 0, 0, 1, 1)

        # Add location button on header bar
        box = Gtk.Box()
        box.get_style_context().add_class("header-cell-box")
        btn = Gtk.Button(_("New Location"))
        btn.set_relief(Gtk.ReliefStyle.NONE)
        btn.get_style_context().add_class("header-cell-btn")
        btn.connect("clicked", self.dialog_add)
        box.add(btn)
        self.grid.attach(box, 1, 0, 1, 1)

        location_list = self.params.locations

        i = 0
        for item in location_list:
            i += 1

            prefix = "\t"*(len(item["sequence"]) - 1)
            label_string = "{0}{1}".format(prefix, item["sequence"][-1])

            label = Gtk.Label(label_string, xalign=0)
            label.get_style_context().add_class("medicine-item-cell")
            if item["rescue_bag"]:
                label.get_style_context().add_class("rescue-bag-item")
            elif item["id"] < 100:
                label.get_style_context().add_class("location-reserved-item")
            self.grid.attach(label, 0, i, 1, 1)

            # We cannot destroy a rescue bag tagged location
            if not item["rescue_bag"]:
                self.location_row_buttons(item, i)
            else:
                label = Gtk.Label("")
                label.get_style_context().add_class("medicine-item-buttons")
                self.grid.attach(label, 1, i, 1, 1)

            # Check if it is a top level item
            if len(item["sequence"]) == 1:
                label.get_style_context().add_class("location-parent")

        query_count_all()

    def refresh_grid(self):
        # Destroy all ScrolledWindow children
        children = self.scrolled.get_children()
        for child in children:
            child.destroy()

        # Re-create the Grid and attach it to the ScrolledWindow
        self.params.refresh_locations()

        self.build_grid()
        self.scrolled.show_all()

    def dialog_delete(self, source, data):
        builder = Gtk.Builder.new_from_file(utils.get_template("location_delete.glade"))
        dialog = builder.get_object("dialog")

        label_string = " > ".join(data["sequence"])

        label = builder.get_object("location")
        label.set_label(label_string)

        builder.connect_signals({
            "on-response": (self.response_delete, data["id"], dialog, builder),
            "on-cancel": (utils.dialog_destroy, dialog)
        })

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def dialog_modify(self, source, data):
        builder = Gtk.Builder.new_from_file(utils.get_template("location_add.glade"))
        dialog = builder.get_object("dialog")

        location_combo = builder.get_object("parent")

        utils.location_combo(
            location_combo,
            locations=self.params.locations,
            active=data["parent"],
            empty=True,
            exclude=[data["id"]]
            )

        name = builder.get_object("name")
        name.set_text(data["sequence"][-1])

        btn_modify = builder.get_object("btn_response")
        btn_modify.set_label(_("Modify this location"))

        builder.connect_signals({
            "on-response": (self.response_modify, data["id"], dialog, builder),
            "on-cancel": (utils.dialog_destroy, dialog)
        })

        query_count_all()

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def dialog_add(self, source):
        log.debug("Add location")

        builder = Gtk.Builder.new_from_file(utils.get_template("location_add.glade"))
        dialog = builder.get_object("dialog")

        location_combo = builder.get_object("parent")
        utils.location_combo(
            location_combo,
            locations=self.params.locations,
            empty=True
            )

        builder.connect_signals({
            "on-response": (self.response_add, dialog, builder),
            "on-cancel": (utils.dialog_destroy, dialog)
        })

        query_count_all()

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def response_add(self, source, dialog, builder):
        fields = {
            "entry": [
                "name"
            ],
            "combobox": [
                "parent"
            ]
        }

        cleaned_data = utils.get_form_data(LocationForm, builder, fields)
        if cleaned_data is None:
            return

        if cleaned_data["parent_id"] == 0:
            cleaned_data["parent_id"] = None

        Location.objects.create(
            parent_id=cleaned_data["parent_id"],
            name=cleaned_data["name"]
        )

        dialog.destroy()
        self.refresh_grid()

        query_count_all()

    def response_modify(self, source, location_id, dialog, builder):
        fields = {
            "entry": [
                "name"
            ],
            "combobox": [
                "parent"
            ]
        }

        cleaned_data = utils.get_form_data(LocationForm, builder, fields)
        if cleaned_data is None:
            return

        if cleaned_data["parent_id"] == 0:
            cleaned_data["parent_id"] = None

        location = Location.objects.get(id=location_id)
        location.name = cleaned_data["name"]
        location.parent_id = cleaned_data["parent_id"]
        location.save()

        dialog.destroy()
        self.refresh_grid()

        query_count_all()

    def response_delete(self, source, location_id, dialog, builder):
        location = Location.objects.get(id=location_id)
        location.delete()
        Location.objects.rebuild()

        dialog.destroy()
        self.refresh_grid()

        query_count_all()
