# -*- coding: utf-8 -*-
"""RescueBag GTK view."""
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk, GLib

from django.utils.translation import gettext as _

from pharmaship.core.utils import log, query_count_all

from pharmaship.inventory.models import RescueBag, Location
from pharmaship.inventory.forms import RescueBagForm
from pharmaship.inventory.parsers.rescue_bag import parser

from pharmaship.gui import utils, widgets


NC_TEXT_TEMPLATE = "<span foreground='darkred' weight='bold' style='normal'>{0} {1}</span>"


class View:
    def __init__(self, window):
        self.window = window
        self.params = window.params

        self.builder = Gtk.Builder.new_from_file(utils.get_template("sidebar_layout.glade"))

        self.stack = self.builder.get_object("stack")

        # For recording the open equipments in the grid
        self.toggled = {
            0: False
        }

        self.children = {}

    def refresh_single_grid(self, visible_child_name):
        try:
            visible_bag_id = int(visible_child_name.split("-")[-1])
        except ValueError as error:
            log.error("Wrong child name (not integer found). %s", error)
            return

        child_builder = self.children[visible_bag_id]

        grid = child_builder.get_object("grid")
        for child in grid.get_children():
            child.destroy()

        data = parser(self.params)

        # Toggle item
        toggle_row_num = None
        if self.toggled[visible_bag_id]:
            toggle_row_num = self.toggled[visible_bag_id][0] - 1

        # Reset toggled value
        self.toggled[visible_bag_id] = False

        self.build_grid(child_builder, data, visible_bag_id, toggle_row_num)
        return

    def refresh_grid(self, single=False):
        visible_child_name = self.stack.get_visible_child_name()

        # Refresh only the current page
        if single:
            self.refresh_single_grid(visible_child_name)
            return

        # We refresh all the view
        for item in self.stack.get_children():
            item.destroy()

        rescue_bags = RescueBag.objects.all().order_by("name").prefetch_related("location")

        data = parser(self.params)
        self.build_full_list(data)
        self.build_bags(data, rescue_bags)

        self.stack.set_visible_child_name(visible_child_name)

    def create_main_layout(self):
        box = self.builder.get_object("main-box")
        # self.scrolled.add(box)
        self.window.layout.pack_start(box, True, True, 0)

        self.window.layout.show_all()

        # Get setting
        self.setting = self.params.setting

        if self.setting.rescue_bag == 0:
            return

        rescue_bags = RescueBag.objects.all().order_by("name").prefetch_related("location")

        # Create the missing first aid kits
        count = rescue_bags.count()
        missing = self.setting.rescue_bag - count

        if missing > 0:
            log.info("Missing some rescue bag instances. Creating...")
            for i in range(missing):
                location = Location.objects.create(
                    name="Rescue Bag {0}".format(count + i),
                    parent_id=0,
                    is_rescue_bag=True
                )

                RescueBag.objects.create(
                    name="Rescue Bag {0}".format(count + i),
                    location_id=location.id
                    )

            rescue_bags = RescueBag.objects.all().order_by("name").prefetch_related("location")

        data = parser(self.params)
        # Create the all bags page
        self.build_full_list(data)

        self.build_bags(data, rescue_bags)

    def build_full_list(self, data):
        child_builder = Gtk.Builder.new_from_file(utils.get_template("rescue_bag.glade"))
        # child = child_builder.get_object("main-box")
        child = child_builder.get_object("child-scrolled")

        # Destroy the top grid containing rescue bag edit form
        top_grid = child_builder.get_object("top-grid")
        top_grid.destroy()

        self.build_full_grid(child_builder, data["all"])
        self.stack.add_titled(child, "all", _("All rescue bags"))
        self.children[0] = child_builder

    def build_full_grid(self, builder, data, toggle_row_num=None):
        grid = builder.get_object("grid")

        label = Gtk.Label(_("Name"), xalign=0)
        label.set_hexpand(True)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 0, 0, 1, 1)

        label = Gtk.Label(_("Remark"), xalign=0)
        label.set_hexpand(True)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 1, 0, 1, 1)

        label = Gtk.Label(_("Expiry"), xalign=0.5)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 2, 0, 1, 1)

        label = Gtk.Label(_("Quantity"), xalign=0.5)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 3, 0, 1, 1)

        label = Gtk.Label("", xalign=0)
        label.get_style_context().add_class("header-cell")
        # Size request because by default the colum content is "hidden"
        label.set_size_request(45, -1)
        grid.attach(label, 4, 0, 1, 1)

        i = 0
        toggle_item = None

        for element in data["elements"]:
            i += 1

            if toggle_row_num and toggle_row_num == i:
                toggle_item = element

            label = Gtk.Label(element["name"], xalign=0)
            label.set_line_wrap(True)
            label.set_lines(1)
            label.set_line_wrap_mode(2)
            label.get_style_context().add_class("item-cell")
            evbox = widgets.EventBox(element, self.toggle_item, 5, i)
            evbox.add(label)
            grid.attach(evbox, 0, i, 1, 1)

            label = Gtk.Label(element["remark"], xalign=0)
            label.set_line_wrap(True)
            label.set_lines(1)
            label.set_line_wrap_mode(2)
            label.get_style_context().add_class("item-cell")
            label.get_style_context().add_class("article-remark")
            evbox = widgets.EventBox(element, self.toggle_item, 5, i)
            evbox.add(label)
            grid.attach(evbox, 1, i, 1, 1)

            date_display = ""
            if len(element["exp_dates"]) > 0 and None not in element["exp_dates"]:
                date_display = min(element["exp_dates"]).strftime("%Y-%m-%d")

            label = Gtk.Label(date_display, xalign=0.5)
            label.get_style_context().add_class("item-cell")
            label.get_style_context().add_class("text-mono")
            if element["has_date_expired"]:
                label.get_style_context().add_class("article-expired")
            elif element["has_date_warning"]:
                label.get_style_context().add_class("article-warning")
            evbox = widgets.EventBox(element, self.toggle_item, 5, i)
            evbox.add(label)
            grid.attach(evbox, 2, i, 1, 1)

            label = Gtk.Label(xalign=0.5)
            label.set_markup("{0}<small>/{1}</small>".format(element["quantity"], element["required_quantity"]))
            label.get_style_context().add_class("item-cell")
            label.get_style_context().add_class("text-mono")
            # Change style if equipment has articles with non-conformity
            if element["has_nc"]:
                label.get_style_context().add_class("item-nc-quantity")
            # If quantity is less than required, affect corresponding style
            if element["quantity"] < element["required_quantity"]:
                label.get_style_context().add_class("article-expired")
            evbox = widgets.EventBox(element, self.toggle_item, 5, i)
            evbox.add(label)
            grid.attach(evbox, 3, i, 1, 1)

            # Set tooltip to give information on allowances requirements
            tooltip_text = []
            for item in element["allowance"]:
                tooltip_text.append("<b>{0}</b> ({1})".format(item["name"], item["quantity"]))
            label.set_tooltip_markup("\n".join(tooltip_text))

            if element["picture"]:
                # Button box for actions
                linked_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                linked_btn.get_style_context().add_class("linked")
                linked_btn.get_style_context().add_class("article-item-buttons")
                evbox = widgets.EventBox(element, self.toggle_item, 5, i)
                evbox.add(linked_btn)
                grid.attach(evbox, 4, i, 1, 1)

                # Picture
                picture = element["picture"]
                btn_picture = widgets.ButtonWithImage("image-x-generic-symbolic", tooltip=_("View picture"), connect=utils.picture_frame, data=picture)
                linked_btn.pack_end(btn_picture, False, True, 0)
            else:
                label = Gtk.Label("", xalign=0.5)
                label.get_style_context().add_class("item-cell")
                evbox = widgets.EventBox(element, self.toggle_item, 5, i)
                evbox.add(label)
                grid.attach(evbox, 4, i, 1, 1)

        # Toggle if active
        if toggle_row_num and toggle_item:
            self.toggle_item(
                source=None,
                grid=grid,
                element=toggle_item,
                row_num=toggle_row_num,
                bag_id=0)

        grid.show_all()

        query_count_all()

    def build_bags(self, data, bags):
        # Get the location_id of all bags to avoid the possibility to select a
        # bag as a location.
        exclude_ids = bags.values_list("location_id", flat=True)

        for bag in bags:
            # Create a page
            child_builder = Gtk.Builder.new_from_file(utils.get_template("rescue_bag.glade"))
            # child = child_builder.get_object("main-box")
            child = child_builder.get_object("child-scrolled")

            child_builder.connect_signals({
                "btn-save-clicked": (self.save_bag, child_builder, bag),
                "btn-cancel-clicked": (self.cancel, child_builder),
                "btn-modify-clicked": (self.enable_modify, child_builder)
            })

            name = child_builder.get_object("name")
            name.set_text(bag.name)
            name.set_sensitive(False)

            location_combo = child_builder.get_object("location")
            location_combo.set_sensitive(False)
            utils.location_combo(
                combo=location_combo,
                locations=self.params.locations,
                active=bag.location.parent_id,
                exclude=exclude_ids)

            btn_save = child_builder.get_object("btn-save")
            btn_save.hide()

            self.toggled[bag.id] = False
            self.build_grid(child_builder, data, bag)
            self.stack.add_titled(child, "rescue-bag-{0}".format(bag.id), bag.name)
            self.children[bag.id] = child_builder

    def build_grid(self, builder, data, bag, toggle_row_num=None):
        grid = builder.get_object("grid")

        label = Gtk.Label(_("Name"), xalign=0)
        label.set_hexpand(True)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 0, 0, 1, 1)

        label = Gtk.Label(_("Remark"), xalign=0)
        label.set_hexpand(True)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 1, 0, 1, 1)

        label = Gtk.Label(_("Expiry"), xalign=0.5)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 2, 0, 1, 1)

        label = Gtk.Label(_("Quantity"), xalign=0.5)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 3, 0, 1, 1)

        label = Gtk.Label("", xalign=0)
        label.get_style_context().add_class("header-cell")
        # Size request because by default the colum content is "hidden"
        label.set_size_request(45, -1)
        grid.attach(label, 4, 0, 1, 1)

        i = 0
        toggle_item = None

        for element in data[bag.id]["elements"]:
            i += 1

            if toggle_row_num and toggle_row_num == i:
                toggle_item = element

            label = Gtk.Label(element["name"], xalign=0)
            label.set_line_wrap(True)
            label.set_lines(1)
            label.set_line_wrap_mode(2)
            label.get_style_context().add_class("item-cell")
            evbox = widgets.EventBox(element, self.toggle_item, 5, i)
            evbox.add(label)
            grid.attach(evbox, 0, i, 1, 1)

            label = Gtk.Label(element["remark"], xalign=0)
            label.set_line_wrap(True)
            label.set_lines(1)
            label.set_line_wrap_mode(2)
            label.get_style_context().add_class("item-cell")
            label.get_style_context().add_class("article-remark")
            evbox = widgets.EventBox(element, self.toggle_item, 5, i)
            evbox.add(label)
            grid.attach(evbox, 1, i, 1, 1)

            date_display = ""
            if len(element["exp_dates"]) > 0 and None not in element["exp_dates"]:
                date_display = min(element["exp_dates"]).strftime("%Y-%m-%d")

            label = Gtk.Label(date_display, xalign=0.5)
            label.get_style_context().add_class("item-cell")
            label.get_style_context().add_class("text-mono")
            if element["has_date_expired"]:
                label.get_style_context().add_class("article-expired")
            elif element["has_date_warning"]:
                label.get_style_context().add_class("article-warning")
            evbox = widgets.EventBox(element, self.toggle_item, 5, i)
            evbox.add(label)
            grid.attach(evbox, 2, i, 1, 1)

            label = Gtk.Label(element["quantity"], xalign=0.5)
            label.get_style_context().add_class("item-cell")
            label.get_style_context().add_class("text-mono")
            # Change style if equipment has articles with non-conformity
            if element["has_nc"]:
                label.get_style_context().add_class("item-nc-quantity")
            evbox = widgets.EventBox(element, self.toggle_item, 5, i)
            evbox.add(label)
            grid.attach(evbox, 3, i, 1, 1)

            # Set tooltip to give information on allowances requirements
            tooltip_text = []
            for item in element["allowance"]:
                tooltip_text.append("<b>{0}</b> ({1})".format(item["name"], item["quantity"]))
            label.set_tooltip_markup("\n".join(tooltip_text))

            if element["picture"]:
                # Button box for actions
                linked_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                linked_btn.get_style_context().add_class("linked")
                linked_btn.get_style_context().add_class("equipment-item-buttons")
                evbox = widgets.EventBox(element, self.toggle_item, 5, i)
                evbox.add(linked_btn)
                grid.attach(evbox, 4, i, 1, 1)

                # Picture
                picture = element["picture"]
                btn_picture = widgets.ButtonWithImage("image-x-generic-symbolic", tooltip=_("View picture"), connect=utils.picture_frame, data=picture)
                linked_btn.pack_end(btn_picture, False, True, 0)
            else:
                label = Gtk.Label("", xalign=0.5)
                label.get_style_context().add_class("item-cell")
                evbox = widgets.EventBox(element, self.toggle_item, 5, i)
                evbox.add(label)
                grid.attach(evbox, 4, i, 1, 1)

        # Toggle if active
        if toggle_row_num and toggle_item:
            self.toggle_item(
                source=None,
                grid=grid,
                element=toggle_item,
                row_num=toggle_row_num,
                bag_id=bag.id)

        grid.show_all()

        query_count_all()

    def toggle_item(self, source, grid, element, row_num, bag_id=0):
        # If already toggled, destroy the toggled part
        if self.toggled[bag_id] and self.toggled[bag_id][0] > 0:
            for i in range(self.toggled[bag_id][1] - self.toggled[bag_id][0] + 1):
                grid.remove_row(self.toggled[bag_id][0])
            # No need to recreate the widget, we just want to hide
            if row_num + 1 == self.toggled[bag_id][0]:
                self.toggled[bag_id] = False
                return True

        # Need to create the content
        new_row = row_num + 1
        grid.insert_row(new_row)

        # Header row
        label = Gtk.Label(_("Commercial Name"), xalign=0)
        label.set_hexpand(True)
        label.get_style_context().add_class("article-header-cell")
        grid.attach(label, 0, 0 + new_row, 1, 1)

        label = Gtk.Label(_("Remarks"), xalign=0)
        label.get_style_context().add_class("article-header-cell")
        grid.attach(label, 1, 0 + new_row, 1, 1)

        label = Gtk.Label(_("Expiry"), xalign=0.5)
        label.get_style_context().add_class("article-header-cell")
        grid.attach(label, 2, 0 + new_row, 1, 1)

        label = Gtk.Label(_("Quantity"), xalign=0.5)
        label.get_style_context().add_class("article-header-cell")
        grid.attach(label, 3, 0 + new_row, 1, 1)

        label = Gtk.Label("", xalign=1)
        label.get_style_context().add_class("article-header-cell")
        grid.attach(label, 4, 0 + new_row, 1, 1)

        # Get related articles
        i = new_row
        for item in element["contents"]:

            i += 1
            grid.insert_row(i)

            label = Gtk.Label(item["name"], xalign=0)
            label.set_hexpand(True)
            label.get_style_context().add_class("article-item-cell-name")
            label.get_style_context().add_class("article-item-cell")
            grid.attach(label, 0, i, 1, 1)

            # Remark field (mainly used for non-compliance)
            remark_text = []

            if "packaging" in item["nc"] and item["nc"]["packaging"]:
                remark_text.append(NC_TEXT_TEMPLATE.format(_("Non-compliant packaging:"), item["nc"]["packaging"]))
            if "composition" in item["nc"] and item["nc"]["composition"]:
                remark_text.append(NC_TEXT_TEMPLATE.format(_("Non-compliant composition:"), item["nc"]["composition"]))
            if "molecule" in item["nc"] and item["nc"]["molecule"]:
                remark_text.append(NC_TEXT_TEMPLATE.format(_("Non-compliant molecule:"), item["nc"]["molecule"]))
            if item["remark"]:
                remark_text.append(item["remark"])

            label = Gtk.Label(xalign=0)
            label.set_markup("\n".join(remark_text))
            label.get_style_context().add_class("article-item-cell")
            label.get_style_context().add_class("article-remark")

            grid.attach(label, 1, i, 1, 1)

            if item["exp_date"]:
                label = Gtk.Label(item["exp_date"].strftime("%Y-%m-%d"), xalign=0.5)
                label.get_style_context().add_class("text-mono")
            else:
                label = Gtk.Label()
            label.get_style_context().add_class("article-item-cell")

            # If expiry is soon or due, affect corresponding style
            if item["expired"]:
                label.get_style_context().add_class("article-expired")
            elif item["warning"]:
                label.get_style_context().add_class("article-warning")
            grid.attach(label, 2, i, 1, 1)

            label = Gtk.Label(item["quantity"], xalign=0.5)
            label.get_style_context().add_class("article-item-cell")
            label.get_style_context().add_class("text-mono")
            grid.attach(label, 3, i, 1, 1)

            label = Gtk.Label("", xalign=1)
            label.get_style_context().add_class("article-item-cell")
            grid.attach(label, 4, i, 1, 1)

        i += 1
        grid.insert_row(i)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.get_style_context().add_class("article-btn-add")
        if element["type"] == "molecule":
            button.set_action_name("app.medicines")
            button.set_action_target_value(GLib.Variant("i", element["id"]))
            label = Gtk.Label(_("Update in the medicine view"), xalign=0)
        elif element["type"] == "equipment":
            button.set_action_name("app.equipment")
            button.set_action_target_value(GLib.Variant("i", element["id"]))
            label = Gtk.Label(_("Update in the equipment view"), xalign=0)
        else:
            label = Gtk.Label(_("Edit this item in the dedicated view"), xalign=0)
        button.add(label)
        box.add(button)
        box.get_style_context().add_class("article-item-cell-add")
        grid.attach(box, 0, i, 1, 1)

        # Empty row for styling purpose
        label = Gtk.Label("")
        label.get_style_context().add_class("article-item-cell-add")
        grid.attach(label, 1, i, 4, 1)

        grid.show_all()
        self.toggled[bag_id] = (new_row, i)
        # log.info("Size %s, %s", linked_btn.get_preferred_size().minimum_size.width, linked_btn.get_preferred_size().natural_size.width)
        query_count_all()

    def save_bag(self, source, builder, bag):
        fields = {
            "entry": [
                "name"
            ],
            "combobox": [
                "location"
            ]
        }

        cleaned_data = utils.get_form_data(RescueBagForm, builder, fields)
        if cleaned_data is None:
            return

        # Save location
        bag.location.parent_id = cleaned_data["location_id"]
        bag.location.name = cleaned_data["name"]
        bag.location.save()
        # Save rescue bag
        bag.name = cleaned_data["name"]
        bag.save()

        child = self.stack.get_child_by_name("rescue-bag-{0}".format(bag.id))
        self.stack.child_set_property(child, "title", cleaned_data["name"])

        self.cancel(source, builder)

    def enable_modify(self, source, builder):
        btn_save = builder.get_object("btn-save")
        btn_save.show()

        btn_modify = builder.get_object("btn-modify")
        btn_modify.hide()

        btn_cancel = builder.get_object("btn-cancel")
        btn_cancel.set_sensitive(True)

        name = builder.get_object("name")
        name.set_sensitive(True)

        location = builder.get_object("location")
        location.set_sensitive(True)

    def cancel(self, source, builder):
        btn_save = builder.get_object("btn-save")
        btn_save.hide()

        btn_modify = builder.get_object("btn-modify")
        btn_modify.show()

        btn_cancel = builder.get_object("btn-cancel")
        btn_cancel.set_sensitive(False)

        name = builder.get_object("name")
        name.set_sensitive(False)

        location = builder.get_object("location")
        location.set_sensitive(False)
