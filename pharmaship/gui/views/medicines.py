# -*- coding: utf-8 -*-
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk

from django.utils.translation import gettext as _

from pharmaship.core.utils import log, query_count_all

from pharmaship.inventory import models
from pharmaship.inventory import forms
from pharmaship.inventory.parsers.medicines import parser

from pharmaship.gui import utils
from pharmaship.gui.utils import ButtonWithImage, EntryMasked


DATE_MASK = {
    "format": "____-__-__",
    "regex": None,
    "datetime": "%Y-%m-%d",
    "allowed_chars": "0123456789"
}

NC_TEXT_TEMPLATE = "<span foreground='darkred' weight='bold' style='normal'>{0} {1}</span>"


class View:
    def __init__(self, window):
        self.window = window
        self.params = window.params
        self.builder = window.builder
        # For recording the open molecules in the grid
        self.toggled = False

    def refresh_grid(self):
        # Get present scroll position
        position = self.scrolled.get_vadjustment().get_value()

        # The Gtk.ScrolledWindow adds automatically a Gtk.Viewport for Gtk.grid
        # Destroy all viewport children
        viewport = self.scrolled.get_children()[0]
        for child in viewport.get_children():
            child.destroy()

        toggle_row_num = None
        if self.toggled:
            toggle_row_num = self.toggled[0] - 1

        # Reset toggled value
        self.toggled = False

        # Re-create the Grid and attach it to the viewport
        grid = self.create_grid(toggle_row_num)

        viewport.add(grid)
        viewport.show_all()
        viewport.get_vadjustment().set_value(position)

    def create_grid(self, toggle_row_num=None):
        grid = Gtk.Grid()

        # Header
        label = Gtk.Label(_("Name"), xalign=0)
        label.set_hexpand(True)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 0, 0, 1, 1)
        label = Gtk.Label(_("Route of administration"), xalign=0)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 1, 0, 1, 1)
        label = Gtk.Label(_("Form/Dosage"), xalign=0)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 2, 0, 1, 1)
        label = Gtk.Label(_("Location"), xalign=0)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 3, 0, 1, 1)
        label = Gtk.Label(_("Expiry"), xalign=0.5)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 4, 0, 1, 1)
        label = Gtk.Label(_("Quantity"), xalign=0.5)
        label.get_style_context().add_class("header-cell")
        grid.attach(label, 5, 0, 1, 1)
        label = Gtk.Label("", xalign=0)
        label.get_style_context().add_class("header-cell")
        # Size request because by default the colum content is "hidden"
        label.set_size_request(125, -1)
        grid.attach(label, 6, 0, 1, 1)

        data = parser(self.params)

        i = 0
        toggle_molecule = None
        for group in data:
            i += 1

            label = Gtk.Label(group, xalign=0)
            label.get_style_context().add_class("group-cell")
            grid.attach(label, 0, i, 7, 1)

            for molecule in data[group]:
                # Do not show orphans without quantity
                if molecule["required_quantity"] == 0 and molecule["quantity"] == 0:
                    continue

                i += 1

                # If toggle_row_num is defined, record first the molecule then,
                # when all construction is done, call toggle_medicine function.
                if toggle_row_num and toggle_row_num == i:
                    toggle_molecule = molecule

                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                button = Gtk.Button()
                label = Gtk.Label(molecule["name"], xalign=0)
                label.set_line_wrap(True)
                label.set_lines(1)
                label.set_line_wrap_mode(2)
                button.add(label)
                button.set_relief(Gtk.ReliefStyle.NONE)
                button.get_style_context().add_class("item-cell-btn")
                # button.get_style_context().add_class("item-cell")
                button.connect("clicked", self.toggle_medicine, grid, molecule, i)
                box.pack_start(button, True, True, 0)
                box.get_style_context().add_class("item-cell-name")
                grid.attach(box, 0, i, 1, 1)

                label = Gtk.Label(molecule["roa"], xalign=0)
                label.get_style_context().add_class("item-cell")
                grid.attach(label, 1, i, 1, 1)

                label = Gtk.Label("{0} ({1})".format(molecule["dosage_form"], molecule["composition"]), xalign=0)
                label.get_style_context().add_class("item-cell")
                label.set_line_wrap(True)
                label.set_lines(1)
                label.set_line_wrap_mode(2)
                grid.attach(label, 2, i, 1, 1)

                # Get list of locations
                locations_len = len(molecule["locations"])
                if locations_len == 0:
                    locations_display = ""
                elif locations_len >= 1:
                    molecule["locations"].sort()
                    locations_display = molecule["locations"][0]
                if locations_len > 1:
                    locations_display += ", ..."

                label = Gtk.Label(locations_display, xalign=0)
                label.set_line_wrap(True)
                label.set_lines(1)
                label.set_line_wrap_mode(2)
                label.get_style_context().add_class("item-cell")
                grid.attach(label, 3, i, 1, 1)

                # Get first expiry date
                date_display = ""
                if len(molecule["exp_dates"]) > 0:
                    date_display = min(molecule["exp_dates"]).strftime("%Y-%m-%d")

                label = Gtk.Label(date_display, xalign=0.5)
                label.get_style_context().add_class("item-cell")
                label.get_style_context().add_class("text-mono")
                if molecule["has_date_expired"]:
                    label.get_style_context().add_class("medicine-expired")
                elif molecule["has_date_warning"]:
                    label.get_style_context().add_class("medicine-warning")
                grid.attach(label, 4, i, 1, 1)

                # label = Gtk.Label("{0}/{1}".format(molecule["quantity"], molecule["required_quantity"]), xalign=0.5)
                label = Gtk.Label(xalign=0.5)
                label.set_markup("{0}<small>/{1}</small>".format(molecule["quantity"], molecule["required_quantity"]))
                label.get_style_context().add_class("item-cell")
                label.get_style_context().add_class("text-mono")
                # Change style if molecule has medicines with non-conformity
                if molecule["has_nc"]:
                    label.get_style_context().add_class("item-nc-quantity")
                # If quantity is less than required, affect corresponding style
                if molecule["quantity"] < molecule["required_quantity"]:
                    label.get_style_context().add_class("medicine-expired")
                grid.attach(label, 5, i, 1, 1)

                # Set tooltip to give information on allowances requirements
                tooltip_text = []
                for item in molecule["allowance"]:
                    tooltip_text.append("<b>{0}</b> ({1})".format(item["name"], item["quantity"]))
                label.set_tooltip_markup("\n".join(tooltip_text))

                # Empty item for styling purpose
                label = Gtk.Label("", xalign=0.5)
                label.get_style_context().add_class("item-cell")
                grid.attach(label, 6, i, 1, 1)

        # Toggle if active
        if toggle_row_num and toggle_molecule:
            self.toggle_medicine(source=None, grid=grid, molecule=toggle_molecule, row_num=toggle_row_num)

        query_count_all()

        return grid

    def create_main_layout(self):
        # Create content
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.props.hscrollbar_policy = Gtk.PolicyType.NEVER
        # No overlay of the scrollbar
        self.scrolled.props.overlay_scrolling = False
        self.window.layout.pack_start(self.scrolled, True, True, 0)
        grid = self.create_grid()
        self.scrolled.add(grid)

    def dialog_use(self, source, medicine):
        builder = Gtk.Builder.new_from_file(utils.get_template("medicine_use.glade"))
        dialog = builder.get_object("dialog")

        # Set the current values
        name = builder.get_object("name")
        name.set_text("{0} ({1})".format(medicine["name"], medicine["exp_date"]))

        remaining = builder.get_object("remaining")
        remaining.set_value(medicine["quantity"])

        remaining_adjustment = builder.get_object("remaining_adjustment")
        remaining_adjustment.set_lower(0)
        remaining_adjustment.set_upper(medicine["quantity"])

        quantity_adjustment = builder.get_object("quantity_adjustment")
        quantity_adjustment.set_lower(0)
        quantity_adjustment.set_upper(medicine["quantity"])

        # quantity = builder.get_object("quantity")
        # quantity.connect("value-changed", self.medicine_quantity_changed, medicine["quantity"], remaining)

        builder.connect_signals({
            "on-response": (self.response_use, dialog, medicine, builder),
            "on-cancel": (utils.dialog_destroy, dialog),
            "quantity-changed": (utils.item_quantity_changed, remaining)
        })

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def dialog_modify(self, source, medicine):
        builder = Gtk.Builder.new_from_file(utils.get_template("medicine_add.glade"))
        dialog = builder.get_object("dialog")

        label = builder.get_object("molecule")
        label.set_text(medicine["molecule"]["name"])

        btn_add = builder.get_object("btn_response")
        btn_add.set_label(_("Modify the medicine"))

        location_combo = builder.get_object("location")
        utils.location_combo(
            combo=location_combo,
            locations=self.params.locations,
            active=medicine["location"]["id"]
            )

        # Set the current values
        name = builder.get_object("name")
        name.set_text(medicine["name"])

        quantity = builder.get_object("quantity")
        quantity.set_value(medicine["quantity"])

        # exp_date = builder.get_object("exp_date")
        exp_date = builder.get_object("exp_date_raw")
        exp_date = utils.grid_replace(exp_date, EntryMasked(mask=DATE_MASK))
        builder.expose_object("exp_date", exp_date)
        date_display = medicine["exp_date"].strftime("%Y-%m-%d")
        exp_date.get_buffer().set_text(date_display, len(date_display))

        if medicine["remark"]:
            remark = builder.get_object("remark")
            remark.set_text(medicine["remark"])

        if medicine["nc_composition"]:
            nc_composition = builder.get_object("nc_composition")
            nc_composition.set_text(medicine["nc_composition"])
        if medicine["nc_molecule"]:
            nc_molecule = builder.get_object("nc_molecule")
            nc_molecule.set_text(medicine["nc_molecule"])
        # If nc_molecule or nc_composition, open the expander
        if medicine["nc_molecule"] or medicine["nc_composition"]:
            nc_expander = builder.get_object("nc_expander")
            nc_expander.set_expanded(True)

        # Connect signals
        builder.connect_signals({
            "on-response": (self.response_modify, dialog, medicine, builder),
            "on-cancel": (utils.dialog_destroy, dialog)
        })

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def dialog_delete(self, source, medicine):
        builder = Gtk.Builder.new_from_file(utils.get_template("medicine_delete.glade"))
        dialog = builder.get_object("dialog")

        # Set the current values
        name = builder.get_object("name")
        name.set_text("{0} ({1}) - quantity: {2}".format(medicine["name"], medicine["exp_date"], medicine["quantity"]))

        # Delete reason combo box
        reason_combo = builder.get_object("reason")

        utils.reason_combo(reason_combo, expired=medicine["expired"])

        builder.connect_signals({
            "on-response": (self.response_delete, dialog, medicine, builder),
            "on-cancel": (utils.dialog_destroy, dialog)
        })

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def dialog_add(self, source, molecule):
        builder = Gtk.Builder.new_from_file(utils.get_template("medicine_add.glade"))
        dialog = builder.get_object("dialog")

        label = builder.get_object("molecule")
        label.set_text("{0} ({1} - {2})".format(molecule["name"], molecule["dosage_form"], molecule["composition"]))

        # Check if molecule has previous locations to input the latest one as
        # default to ease the input
        active_location = None
        molecule_obj = models.Molecule.objects.get(id=molecule["id"])
        try:
            latest_medicine = molecule_obj.medicines.latest("exp_date")
        except models.Medicine.DoesNotExist:
            latest_medicine = None

        if latest_medicine:
            active_location = latest_medicine.location.id
            log.debug("Found last location: %s", active_location)
        location_combo = builder.get_object("location")
        utils.location_combo(
            combo=location_combo,
            locations=self.params.locations,
            active=active_location
            )

        # By default name = molecule name
        name = builder.get_object("name")
        name.set_text(molecule["name"])

        # Expiry date input mask workaround
        exp_date = builder.get_object("exp_date_raw")
        exp_date = utils.grid_replace(exp_date, EntryMasked(mask=DATE_MASK))
        # exp_date.connect("activate", self.response_add, dialog, molecule, builder)
        builder.expose_object("exp_date", exp_date)

        # Connect signals
        builder.connect_signals({
            # "on-entry-activate": (self.response_add, dialog, molecule, builder),
            "on-response": (self.response_add, dialog, molecule, builder),
            "on-cancel": (utils.dialog_destroy, dialog)
        })

        query_count_all()

        dialog.set_transient_for(self.window)
        dialog.run()

        dialog.destroy()

    def response_add(self, source, dialog, molecule, builder):
        fields = {
            "entry": [
                "name",
                "exp_date",
                "nc_composition",
                "nc_molecule",
                "remark"
            ],
            "combobox": [
                "location"
            ],
            "spinbutton": [
                "quantity"
            ],
            "textview": []
        }

        data = {
            "parent_id": molecule["id"]
        }

        cleaned_data = utils.get_form_data(forms.AddMedicineForm, builder, fields, data)
        if cleaned_data is None:
            return

        # Add the medicine
        medicine = models.Medicine.objects.create(
            name=cleaned_data['name'],
            exp_date=cleaned_data['exp_date'],
            location_id=cleaned_data['location_id'],
            nc_composition=cleaned_data['nc_composition'],
            nc_molecule=cleaned_data['nc_molecule'],
            parent_id=cleaned_data['parent_id'],
            remark=cleaned_data['remark']
            )
        # Add the quantity
        models.QtyTransaction.objects.create(
            transaction_type=1,
            value=cleaned_data["quantity"],
            content_object=medicine
            )

        query_count_all()

        # At the end only
        dialog.destroy()
        # Refresh the list!
        self.refresh_grid()

    def response_modify(self, source, dialog, medicine, builder):
        fields = {
            "entry": [
                "name",
                "exp_date",
                "nc_composition",
                "nc_molecule",
                "remark"
            ],
            "combobox": [
                "location"
            ],
            "spinbutton": [
                "quantity"
            ],
            "textview": []
        }

        cleaned_data = utils.get_form_data(forms.ModifyMedicineForm, builder, fields)
        if cleaned_data is None:
            return

        # Add the medicine
        medicine_obj = models.Medicine.objects.get(id=medicine['id'])
        medicine_obj.name = cleaned_data['name']
        medicine_obj.exp_date = cleaned_data['exp_date']
        medicine_obj.location_id = cleaned_data['location_id']
        medicine_obj.remark = cleaned_data['remark']

        # if cleaned_data['nc_composition']:
        medicine_obj.nc_composition = cleaned_data['nc_composition']
        # if cleaned_data['nc_molecule']:
        medicine_obj.nc_molecule = cleaned_data['nc_molecule']

        medicine_obj.save()

        if cleaned_data["quantity"] != medicine['quantity']:
            # Add the quantity (transaction type STOCK COUNT)
            models.QtyTransaction.objects.create(
                transaction_type=8,
                value=cleaned_data["quantity"],
                content_object=medicine_obj
                )

        query_count_all()

        # At the end only
        dialog.destroy()
        # Refresh the list!
        self.refresh_grid()

    def response_delete(self, source, dialog, medicine, builder):
        invalid = False
        # Get response

        reason_combo = builder.get_object("reason")
        reason = utils.get_reason(reason_combo)

        if reason is None:
            reason_combo.get_style_context().add_class("error-combobox")
            invalid = True

        if invalid:
            return

        # Get the object
        medicine_obj = models.Medicine.objects.get(id=medicine['id'])

        # Reason is Other (error during input ?)
        if reason == 9:
            medicine_obj.delete()

        # Reason is Perished - it is one way to declare as perished, other way
        # is to "use" the medicine
        if reason == 4:
            medicine_obj.used = True
            medicine_obj.save()

            models.QtyTransaction.objects.create(
                transaction_type=4,
                value=0,
                content_object=medicine_obj
            )

        query_count_all()

        # At the end only
        dialog.destroy()
        # Refresh the list!
        self.refresh_grid()

    def response_use(self, source, dialog, medicine, builder):
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
        medicine_obj = models.Medicine.objects.get(id=medicine['id'])
        if medicine["quantity"] == quantity:
            medicine_obj.used = True
            medicine_obj.save()

        models.QtyTransaction.objects.create(
            transaction_type=2,
            value=quantity,
            content_object=medicine_obj
        )

        query_count_all()

        # At the end only
        dialog.destroy()
        # Refresh the list!
        self.refresh_grid()

    def toggle_medicine(self, source, grid, molecule, row_num):
        # log.info("Molecule clicked: %s", molecule)

        # If already toggled, destroy the toggled part
        if self.toggled and self.toggled[0] > 0:
            for i in range(self.toggled[1] - self.toggled[0] + 1):
                grid.remove_row(self.toggled[0])
            # No need to recreate the widget, we just want to hide
            if row_num + 1 == self.toggled[0]:
                self.toggled = False
                return True

        # Need to create the content
        new_row = row_num + 1
        grid.insert_row(new_row)

        # grid = Gtk.Grid()
        # grid.attach(grid, 0, new_row, 6, 1)
        grid = grid

        # Header row
        label = Gtk.Label(_("Commercial Name"), xalign=0)
        label.set_hexpand(True)
        label.get_style_context().add_class("medicine-header-cell")
        grid.attach(label, 0, 0 + new_row, 1, 1)

        label = Gtk.Label(_("Remarks"), xalign=0)
        label.get_style_context().add_class("medicine-header-cell")
        grid.attach(label, 1, 0 + new_row, 2, 1)

        label = Gtk.Label(_("Location"), xalign=0)
        label.get_style_context().add_class("medicine-header-cell")
        grid.attach(label, 3, 0 + new_row, 1, 1)

        label = Gtk.Label(_("Expiry"), xalign=0.5)
        label.get_style_context().add_class("medicine-header-cell")
        grid.attach(label, 4, 0 + new_row, 1, 1)

        label = Gtk.Label(_("Quantity"), xalign=0.5)
        label.get_style_context().add_class("medicine-header-cell")
        grid.attach(label, 5, 0 + new_row, 1, 1)

        label = Gtk.Label(_("Actions"), xalign=1)
        label.get_style_context().add_class("medicine-header-cell")
        grid.attach(label, 6, 0 + new_row, 1, 1)

        # Get related medicines
        medicines = molecule["medicines"]

        i = new_row
        for medicine in medicines:
            i += 1
            grid.insert_row(i)

            label = Gtk.Label(medicine["name"], xalign=0)
            label.set_hexpand(True)
            label.get_style_context().add_class("medicine-item-cell-name")
            label.get_style_context().add_class("medicine-item-cell")
            grid.attach(label, 0, i, 1, 1)

            # Remark field (mainly used for non-compliance)
            remark_text = []

            if medicine["nc_molecule"]:
                remark_text.append(NC_TEXT_TEMPLATE.format(_("Non-compliant molecule:"), medicine["nc_molecule"]))
            if medicine["nc_composition"]:
                remark_text.append(NC_TEXT_TEMPLATE.format(_("Non-compliant composition:"), medicine["nc_composition"]))
            if medicine["remark"]:
                remark_text.append(medicine["remark"])

            label = Gtk.Label(xalign=0)
            label.set_markup("\n".join(remark_text))
            label.get_style_context().add_class("medicine-item-cell")
            label.get_style_context().add_class("medicine-remark")

            grid.attach(label, 1, i, 2, 1)

            label = Gtk.Label(xalign=0)
            label.get_style_context().add_class("medicine-item-cell")
            sequence = medicine["location"]["sequence"]
            if len(sequence) > 1:
                parents = " > ".join(sequence[:-1])
                location_display = "<span foreground=\"#555\">{0} > </span>{1}".format(parents, sequence[-1])
            else:
                location_display = sequence[0]

            label.set_markup(location_display)
            label.set_line_wrap(True)
            label.set_lines(1)
            label.set_line_wrap_mode(2)
            grid.attach(label, 3, i, 1, 1)

            label = Gtk.Label(medicine["exp_date"].strftime("%Y-%m-%d"), xalign=0.5)
            label.get_style_context().add_class("medicine-item-cell")
            label.get_style_context().add_class("text-mono")

            # If expiry is soon or due, affect corresponding style
            if medicine["expired"]:
                label.get_style_context().add_class("medicine-expired")
            elif medicine["warning"]:
                label.get_style_context().add_class("medicine-warning")
            grid.attach(label, 4, i, 1, 1)

            label = Gtk.Label(medicine["quantity"], xalign=0.5)
            label.get_style_context().add_class("medicine-item-cell")
            label.get_style_context().add_class("text-mono")
            grid.attach(label, 5, i, 1, 1)

            # Button box for actions
            linked_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            linked_btn.get_style_context().add_class("linked")
            linked_btn.get_style_context().add_class("medicine-item-buttons")
            # linked_btn.set_halign(Gtk.Align.END)
            grid.attach(linked_btn, 6, i, 1, 1)

            # Use
            btn_use = ButtonWithImage("edit-redo-symbolic", tooltip=_("Use"), connect=self.dialog_use, data=medicine)
            linked_btn.pack_end(btn_use, False, True, 0)
            # Modify
            btn_modify = ButtonWithImage("document-edit-symbolic", tooltip=_("Modify"), connect=self.dialog_modify, data=medicine)
            linked_btn.pack_end(btn_modify, False, True, 0)
            # Delete
            btn_delete = ButtonWithImage("edit-delete-symbolic", tooltip=_("Delete"), connect=self.dialog_delete, data=medicine)
            btn_delete.get_style_context().add_class("medicine-btn-delete")
            linked_btn.pack_end(btn_delete, False, True, 0)

        i += 1
        grid.insert_row(i)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button = Gtk.Button()
        label = Gtk.Label(_("Add a medicine"), xalign=0)
        button.add(label)
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.get_style_context().add_class("medicine-btn-add")
        button.connect("clicked", self.dialog_add, molecule)
        box.add(button)
        box.get_style_context().add_class("medicine-item-cell-add")
        grid.attach(box, 0, i, 1, 1)

        # Empty row for styling purpose
        label = Gtk.Label("")
        label.get_style_context().add_class("medicine-item-cell-add")
        grid.attach(label, 1, i, 6, 1)

        grid.show_all()
        self.toggled = (new_row, i)

        query_count_all()
