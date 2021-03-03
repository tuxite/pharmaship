# -*- coding: utf-8 -*-
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk

import json

from django.utils.translation import gettext as _

from pharmaship.core.utils import log, query_count_all

from pharmaship.inventory import models
from pharmaship.inventory import forms
from pharmaship.inventory.parsers.first_aid import parser

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
            visible_kit_id = int(visible_child_name.split("-")[-1])
        except ValueError as error:
            log.error("Wrong child name (not integer found). %s", error)
            return

        child_builder = self.children[visible_kit_id]

        grid = child_builder.get_object("grid")
        for child in grid.get_children():
            child.destroy()

        kits = models.FirstAidKit.objects.filter(id=visible_kit_id).order_by("id").prefetch_related("items")[:self.params.setting.first_aid_kit]
        data = parser(self.params, kits)

        # Toggle item
        toggle_row_num = None
        if self.toggled[visible_kit_id]:
            toggle_row_num = self.toggled[visible_kit_id][0] - 1

        # Reset toggled value
        self.toggled[visible_kit_id] = False

        self.build_grid(child_builder, data[0], toggle_row_num)

        return

    def refresh_grid(self, single=True):
        visible_child_name = self.stack.get_visible_child_name()

        # Refresh only the current page
        if single:
            self.refresh_single_grid(visible_child_name)
            return

        # We refresh all the view
        for item in self.stack.get_children():
            item.destroy()

        self.build_kits()

        self.stack.set_visible_child_name(visible_child_name)

    def create_main_layout(self):
        box = self.builder.get_object("main-box")
        # self.scrolled.add(box)
        self.window.layout.pack_start(box, True, True, 0)

        self.window.layout.show_all()

        # Get setting
        self.setting = self.params.setting

        if self.setting.first_aid_kit == 0:
            return

        first_aid_kits = models.FirstAidKit.objects.order_by("id").prefetch_related("items").all()[:self.params.setting.first_aid_kit]

        # Create the missing first aid kits
        count = first_aid_kits.count()
        missing = self.setting.first_aid_kit - count

        if missing > 0:
            log.info("Missing some first aid kit instances. Creating...")
            for i in range(missing):
                models.FirstAidKit.objects.create(
                    name="First Aid Kit {0}".format(count + i),
                    location_id=0
                    )
            first_aid_kits = None

        self.build_kits(first_aid_kits)

    def build_kits(self, kits=None):
        data = parser(self.params, kits)
        query_count_all()

        for kit in data:
            # Create a page
            child_builder = Gtk.Builder.new_from_file(utils.get_template("first_aid_kit.glade"))
            # child = child_builder.get_object("main-box")
            child = child_builder.get_object("child-scrolled")

            child_builder.connect_signals({
                "btn-save-clicked": (self.save_kit, child_builder, kit),
                "btn-cancel-clicked": (self.cancel, child_builder),
                "btn-modify-clicked": (self.enable_modify, child_builder)
            })

            name = child_builder.get_object("name")
            name.set_text(kit["name"])
            name.set_sensitive(False)

            location_combo = child_builder.get_object("location")
            location_combo.set_sensitive(False)
            utils.location_combo(
                combo=location_combo,
                locations=self.params.locations,
                active=kit["location_id"]
                )

            btn_save = child_builder.get_object("btn-save")
            btn_save.hide()

            self.toggled[kit["id"]] = False
            self.build_grid(child_builder, kit)
            self.stack.add_titled(child, "first-aid-kit-{0}".format(kit["id"]), kit["name"])
            self.children[kit["id"]] = child_builder

    def build_grid(self, builder, data, toggle_row_num=None):
        grid = builder.get_object("grid")

        label = Gtk.Label(_("Name"), xalign=0)
        label.set_hexpand(True)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 0, 0, 2, 1)

        label = Gtk.Label(_("Expiry"), xalign=0.5)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 2, 0, 1, 1)

        label = Gtk.Label(_("Quantity"), xalign=0.5)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 3, 0, 1, 1)

        label = Gtk.Label("", xalign=0)
        label.get_style_context().add_class("header-cell")
        # Size request because by default the colum content is "hidden"
        label.set_size_request(125, -1)
        grid.attach(label, 4, 0, 1, 1)

        i = 0
        toggle_item = None

        for element in data["elements"]:
            # log.debug(item)

            i += 1

            if toggle_row_num and toggle_row_num == i:
                toggle_item = element

            label = Gtk.Label(element["name"], xalign=0)
            label.set_line_wrap(True)
            label.set_lines(1)
            label.set_line_wrap_mode(2)
            label.get_style_context().add_class("item-cell")
            evbox = widgets.EventBox(element, self.toggle_item, 5, i, data["id"])
            evbox.add(label)
            grid.attach(evbox, 0, i, 2, 1)


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
            evbox = widgets.EventBox(element, self.toggle_item, 5, i, data["id"])
            evbox.add(label)
            grid.attach(evbox, 2, i, 1, 1)

            label = Gtk.Label(xalign=0.5)
            label.set_markup("{0}<small>/{1}</small>".format(element["quantity"], element["required_quantity"]))
            label.get_style_context().add_class("item-cell")
            label.get_style_context().add_class("text-mono")
            # Set style according to quantity
            utils.quantity_set_style(label, element)
            evbox = widgets.EventBox(element, self.toggle_item, 5, i, data["id"])
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
                evbox = widgets.EventBox(element, self.toggle_item, 5, i, data["id"])
                evbox.add(linked_btn)
                grid.attach(evbox, 4, i, 1, 1)

                # Picture
                picture = element["picture"]
                btn_picture = widgets.ButtonWithImage("image-x-generic-symbolic", tooltip=_("View picture"), connect=utils.picture_frame, data=picture)
                linked_btn.pack_end(btn_picture, False, True, 0)
            else:
                label = Gtk.Label("", xalign=0.5)
                label.get_style_context().add_class("item-cell")
                evbox = widgets.EventBox(element, self.toggle_item, 5, i, data["id"])
                evbox.add(label)
                grid.attach(evbox, 4, i, 1, 1)

        # Toggle if active
        if toggle_row_num and toggle_item:
            self.toggle_item(
                source=None,
                grid=grid,
                element=toggle_item,
                row_num=toggle_row_num,
                kit_id=data["id"])

        grid.show_all()

        query_count_all()

    def toggle_item(self, source, grid, element, row_num, kit_id):
        # If already toggled, destroy the toggled part
        if self.toggled[kit_id] and self.toggled[kit_id][0] > 0:
            # Remove the active-row CSS class of the parent item
            utils.grid_row_class(grid, self.toggled[kit_id][0] - 1, 5, False)

            for i in range(self.toggled[kit_id][1] - self.toggled[kit_id][0] + 1):
                grid.remove_row(self.toggled[kit_id][0])
            # No need to recreate the widget, we just want to hide
            if row_num + 1 == self.toggled[kit_id][0]:
                self.toggled[kit_id] = False
                return True

        # Add the active-row CSS class
        utils.grid_row_class(grid, row_num, 5)

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

        label = Gtk.Label(_("Actions"), xalign=1)
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

            if item["nc"]:
                nc_obj = json.loads(item["nc"])
                if "packaging" in nc_obj and nc_obj["packaging"]:
                    remark_text.append(NC_TEXT_TEMPLATE.format(_("Non-compliant packaging:"), nc_obj["packaging"]))
                if "composition" in nc_obj and nc_obj["composition"]:
                    remark_text.append(NC_TEXT_TEMPLATE.format(_("Non-compliant composition:"), nc_obj["composition"]))
                if "molecule" in nc_obj and nc_obj["molecule"]:
                    remark_text.append(NC_TEXT_TEMPLATE.format(_("Non-compliant molecule:"), nc_obj["molecule"]))
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

            # Button box for actions
            linked_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            linked_btn.get_style_context().add_class("linked")
            linked_btn.get_style_context().add_class("article-item-buttons")
            # linked_btn.set_halign(Gtk.Align.END)
            grid.attach(linked_btn, 4, i, 1, 1)

            # Use
            btn_use = widgets.ButtonWithImage("edit-redo-symbolic", tooltip="Use", connect=self.dialog_use, data=item)
            linked_btn.pack_end(btn_use, False, True, 0)
            # Modify
            btn_modify = widgets.ButtonWithImage("document-edit-symbolic", tooltip="Modify", connect=self.dialog_modify, data=(item, element["perishable"]))
            linked_btn.pack_end(btn_modify, False, True, 0)
            # Delete
            btn_delete = widgets.ButtonWithImage("edit-delete-symbolic", tooltip="Delete", connect=self.dialog_delete, data=item)
            btn_delete.get_style_context().add_class("article-btn-delete")
            linked_btn.pack_end(btn_delete, False, True, 0)

        i += 1
        grid.insert_row(i)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # Button add from stock
        button = Gtk.Button()
        label = Gtk.Label(_("Transfer an article from stock"), xalign=0)
        button.add(label)
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.get_style_context().add_class("article-btn-add")
        button.connect("clicked", self.dialog_add_from_stock, element)
        box.add(button)
        # Button add new
        button = Gtk.Button()
        label = Gtk.Label(_("Add an article"), xalign=0)
        button.add(label)
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.get_style_context().add_class("article-btn-add-alt")
        button.connect("clicked", self.dialog_add_new, element)
        box.add(button)

        box.get_style_context().add_class("article-item-cell-add")
        grid.attach(box, 0, i, 1, 1)

        # Empty row for styling purpose
        label = Gtk.Label("")
        label.get_style_context().add_class("article-item-cell-add")
        grid.attach(label, 1, i, 4, 1)

        grid.show_all()
        self.toggled[kit_id] = (new_row, i)

        query_count_all()


    def dialog_add_new(self, source, item):
        builder = Gtk.Builder.new_from_file(utils.get_template("subitem_add_new.glade"))
        dialog = builder.get_object("dialog")
        dialog.set_title(_("Add an item"))

        # Preset item name
        label = builder.get_object("name")
        label.set_text(item["name"])
        # Expiry date input mask workaround
        exp_date = builder.get_object("exp_date_raw")
        exp_date = utils.grid_replace(exp_date, widgets.EntryMasked(
            mask=utils.get_date_mask(self.params.setting),
            activate_cb=(self.response_add_new, dialog, item, builder)
            ))
        builder.expose_object("exp_date", exp_date)

        # Connect signals
        builder.connect_signals({
            "on-response": (self.response_add_new, dialog, item, builder),
            "on-cancel": (utils.dialog_destroy, dialog)
        })

        query_count_all()

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()


    def dialog_add_from_stock(self, source, item):
        builder = Gtk.Builder.new_from_file(utils.get_template("subitem_add_from_stock.glade"))
        dialog = builder.get_object("dialog")

        combobox = builder.get_object("item")
        self.subitem_combobox(combobox, item)
        combobox.connect("changed", self.combobox_changed, builder)

        remaining = builder.get_object("remaining")

        quantity = builder.get_object("quantity")
        quantity.connect("changed", self.quantity_changed, remaining)

        quantity_adjustment = builder.get_object("quantity_adjustment")
        quantity_adjustment.set_lower(0)

        remaining_adjustment = builder.get_object("remaining_adjustment")
        remaining_adjustment.set_lower(0)

        # Connect signals
        builder.connect_signals({
            "on-response": (self.response_add_from_stock, dialog, item, builder),
            "on-cancel": (utils.dialog_destroy, dialog)
        })

        query_count_all()

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def combobox_changed(self, source, builder):
        tree_iter = source.get_active_iter()
        if tree_iter is None:
            return

        model = source.get_model()
        item_quantity = model[tree_iter][2]

        remaining = builder.get_object("remaining")
        remaining.set_value(item_quantity)

        quantity = builder.get_object("quantity")
        quantity.set_value(0)

        remaining_adjustment = builder.get_object("remaining_adjustment")
        remaining_adjustment.set_upper(item_quantity)

        quantity_adjustment = builder.get_object("quantity_adjustment")
        quantity_adjustment.set_upper(item_quantity)

    def quantity_changed(self, source, remaining):
        quantity = source.get_value()

        result = source.get_adjustment().get_upper() - quantity
        if result < 0:
            return False
        remaining.set_value(result)

    def subitem_combobox(self, combo, item, active=None):
        # Location combox box setup
        store = Gtk.ListStore(int, str, int, int)

        index = 0
        active_index = -1

        available = item["available"]
        for element in available:
            name = "{0} (exp: {1})".format(
                element["name"],
                element["exp_date"]
                )
            store.append((element["id"], name, element["quantity"], element["type"]))

            if active and element["id"] == active:
                active_index = index

            index += 1

        combo.set_model(store)
        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, "text", 1)
        combo.set_active(active_index)

    def response_add_new(self, source, dialog, item, builder):
        fields = {
            "entry": [
                "name",
                "remark",
                "nc",
                "exp_date"
            ],
            "spinbutton": [
                "quantity",
            ]
        }

        cleaned_data = utils.get_form_data(
            form_class=forms.AddNewSubitemForm,
            builder=builder,
            fields=fields,
            data={"perishable": item["perishable"]}
            )
        if cleaned_data is None:
            return

        # Get the FirstAidKit instance
        try:
            id = int(self.stack.get_visible_child_name().split("-")[-1])
        except ValueError as error:
            log.error("First aid kit ID cannot be found! %s", error)
            return

        try:
            first_aid_kit = models.FirstAidKit.objects.get(id=id)
        except models.FirstAidKit.DoesNotExist as error:
            log.error("First aid kit cannot be found! Wrong ID. %s", error)
            return

        # Create a duplicate of the reference article/medicine
        article = models.FirstAidKitItem.objects.create(
            name=cleaned_data["name"],
            exp_date=cleaned_data["exp_date"],
            kit=first_aid_kit,
            nc=cleaned_data["nc"],
            remark=cleaned_data["remark"],
            content_type_id=item["parent"]["type"],
            object_id=item["parent"]["id"]
        )

        # Create a quantity transaction for FirstAidKitItem
        models.QtyTransaction.objects.create(
            transaction_type=1,
            value=cleaned_data["quantity"],
            content_object=article
            )

        dialog.destroy()

        query_count_all()

        self.refresh_grid()

    def response_add_from_stock(self, source, dialog, item, builder):
        fields = {
            "entry": [
                "remark",
            ],
            "spinbutton": [
                "quantity",
            ],
            "combobox": [
                "item",
            ]
        }

        cleaned_data = utils.get_form_data(forms.AddSubitemForm, builder, fields)
        if cleaned_data is None:
            return

        # Get the FirstAidKit instance
        try:
            id = int(self.stack.get_visible_child_name().split("-")[-1])
        except ValueError as error:
            log.error("First aid kit ID cannot be found! %s", error)
            return

        try:
            first_aid_kit = models.FirstAidKit.objects.get(id=id)
        except models.FirstAidKit.DoesNotExist as error:
            log.error("First aid kit cannot be found! Wrong ID. %s", error)
            return

        selected = None
        for element in item["available"]:
            if element["id"] == cleaned_data["item_id"]:
                selected = element
                break

        if selected is None:
            return

        # Create a duplicate of the reference article/medicine
        article = models.FirstAidKitItem.objects.create(
            name=selected["name"],
            exp_date=selected["exp_date"],
            kit=first_aid_kit,
            nc=json.dumps(selected["nc"]),
            content_type_id=item["parent"]["type"],
            object_id=item["parent"]["id"]
        )

        # Create a quantity transaction for FirstAidKitItem
        models.QtyTransaction.objects.create(
            transaction_type=1,
            value=cleaned_data["quantity"],
            content_object=article
            )

        # Create a new reference article/medicine for "opened" box if necessary
        if utils.check_object_content(selected, cleaned_data["quantity"]):
            object_id = utils.split_object(selected, cleaned_data["quantity"])
        else:
            object_id = cleaned_data["item_id"]

        # Create a quantity transaction for the reference article/medicine
        models.QtyTransaction.objects.create(
            transaction_type=10,
            value=cleaned_data["quantity"],
            object_id=object_id,
            content_type_id=selected["type"]
            )

        dialog.destroy()

        query_count_all()

        self.refresh_grid()

    def save_kit(self, source, builder, kit):
        fields = {
            "entry": [
                "name"
            ],
            "combobox": [
                "location"
            ]
        }

        cleaned_data = utils.get_form_data(forms.FirstAidKitForm, builder, fields)

        if cleaned_data is None:
            return

        try:
            kit_obj = models.FirstAidKit.objects.get(id=kit["id"])
        except models.FirstAidKit.DoesNotExist as error:
            log.error("First aid kit (ID %s) not found.", error)
            return False

        kit_obj.name = cleaned_data["name"]
        kit_obj.location_id = cleaned_data["location_id"]
        kit_obj.save()

        child = self.stack.get_child_by_name("first-aid-kit-{0}".format(kit_obj.id))
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

    def dialog_use(self, source, item):
        builder = Gtk.Builder.new_from_file(utils.get_template("subitem_use.glade"))
        dialog = builder.get_object("dialog")

        # Set the current values
        name = builder.get_object("name")
        name.set_text("{0} ({1})".format(item["name"], item["exp_date"]))

        remaining = builder.get_object("remaining")
        remaining.set_value(item["quantity"])

        remaining_adjustment = builder.get_object("remaining_adjustment")
        remaining_adjustment.set_lower(0)
        remaining_adjustment.set_upper(item["quantity"])

        quantity_adjustment = builder.get_object("quantity_adjustment")
        quantity_adjustment.set_lower(0)
        quantity_adjustment.set_upper(item["quantity"])

        builder.connect_signals({
            "on-response": (self.response_use, dialog, item, builder),
            "on-cancel": (utils.dialog_destroy, dialog),
            "quantity-changed": (utils.item_quantity_changed, remaining)
        })

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def response_use(self, source, dialog, item, builder):
        # Get response
        quantity_obj = builder.get_object("quantity")
        quantity = quantity_obj.get_value()

        if quantity < 0:
            return False

        if quantity == 0:
            # Nothing to do
            dialog.destroy()
            return

        # Get the object
        item_obj = models.FirstAidKitItem.objects.get(id=item['id'])
        if item["quantity"] == quantity:
            item_obj.used = True
            item_obj.save()

        models.QtyTransaction.objects.create(
            transaction_type=2,
            value=quantity,
            content_object=item_obj
        )

        query_count_all()

        # At the end only
        dialog.destroy()
        # Refresh the list!
        self.refresh_grid()

    def dialog_modify(self, source, data):
        item = data[0]
        perishable = data[1]

        builder = Gtk.Builder.new_from_file(utils.get_template("subitem_modify.glade"))
        dialog = builder.get_object("dialog")

        name = builder.get_object("name")
        name.set_text(item["name"])

        quantity = builder.get_object("quantity")
        quantity.set_value(item["quantity"])

        exp_date = builder.get_object("exp_date_raw")
        exp_date = utils.grid_replace(exp_date, widgets.EntryMasked(
            mask=utils.get_date_mask(self.params.setting),
            activate_cb=(self.response_modify, dialog, item, perishable, builder)
            ))

        builder.expose_object("exp_date", exp_date)
        date_display = item["exp_date"].strftime("%Y-%m-%d")
        exp_date.get_buffer().set_text(date_display, len(date_display))

        if item["remark"]:
            remark = builder.get_object("remark")
            remark.set_text(item["remark"])

        if item["nc"]:
            remark = builder.get_object("nc")
            remark.set_text(item["nc"])

        builder.connect_signals({
            "on-response": (self.response_modify, dialog, item, perishable, builder),
            "on-cancel": (utils.dialog_destroy, dialog)
        })

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def response_modify(self, source, dialog, item, perishable, builder):
        fields = {
            "entry": [
                "exp_date",
                "remark",
                "nc"
            ],
            "spinbutton": [
                "quantity"
            ]
        }

        data = {
            "perishable": perishable
        }

        cleaned_data = utils.get_form_data(forms.ModifySubitemForm, builder, fields, data)
        if cleaned_data is None:
            return

        item_obj = models.FirstAidKitItem.objects.get(id=item["id"])
        item_obj.exp_date = cleaned_data["exp_date"]
        item_obj.remark = cleaned_data["remark"]
        item_obj.nc = cleaned_data["nc"]
        item_obj.save()

        if cleaned_data["quantity"] != item['quantity']:
            # Add the quantity (transaction type STOCK COUNT)
            models.QtyTransaction.objects.create(
                transaction_type=8,
                value=cleaned_data["quantity"],
                content_object=item_obj
                )

        query_count_all()

        # At the end only
        dialog.destroy()
        # Refresh the list!
        self.refresh_grid()

    def dialog_delete(self, source, item):
        builder = Gtk.Builder.new_from_file(utils.get_template("subitem_delete.glade"))
        dialog = builder.get_object("dialog")

        # Set the current values
        name = builder.get_object("name")
        name.set_text("{0} ({1}) - quantity: {2}".format(item["name"], item["exp_date"], item["quantity"]))

        # Delete reason combo box
        reason_combo = builder.get_object("reason")

        utils.reason_combo(reason_combo, expired=item["expired"])

        builder.connect_signals({
            "on-response": (self.response_delete, dialog, item, builder),
            "on-cancel": (utils.dialog_destroy, dialog)
        })

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def response_delete(self, source, dialog, item, builder):
        invalid = False
        # Get response
        reason_combo = builder.get_object("reason")
        reason = utils.get_combo_value(reason_combo)

        if reason is None:
            reason_combo.get_style_context().add_class("error-combobox")
            invalid = True

        if invalid:
            return

        # Get the object
        item_obj = models.FirstAidKitItem.objects.get(id=item['id'])

        # Reason is Other (error during input ?)
        if reason == 9:
            item_obj.delete()

        # Reason is Perished - it is one way to declare as perished, other way
        # is to "use" the medicine
        if reason == 4:
            item_obj.used = True
            item_obj.save()

            models.QtyTransaction.objects.create(
                transaction_type=4,
                value=0,
                content_object=item_obj
            )

        query_count_all()

        # At the end only
        dialog.destroy()
        # Refresh the list!
        self.refresh_grid()
