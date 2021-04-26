# -*- coding: utf-8 -*-
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk, GLib

import threading

from django.utils.translation import gettext as _

from pharmaship.inventory.models import Allowance, RescueBag, Location
from pharmaship.inventory.forms import InventorySettingsForm

from pharmaship.core.utils import log, query_count_all
from pharmaship.core.import_data import Importer

from pharmaship.gui.utils import get_form_data, get_builder


class View:
    def __init__(self, window, application):
        self.window = window
        self.params = window.params

        self.application = application

        self.builder = get_builder("allowance_manager.ui")

        self.invalid = False

    def create_main_layout(self):
        # Create content
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.props.hscrollbar_policy = Gtk.PolicyType.NEVER
        # No overlay of the scrollbar
        self.scrolled.props.overlay_scrolling = False
        self.window.layout.pack_start(self.scrolled, True, True, 0)

        box = self.builder.get_object("allowance-box")
        self.scrolled.add(box)

        # Get setting
        self.setting = self.params.setting

        self.build_allowance_tree()
        self.build_form()

        self.window.layout.show_all()

        self.build_action_bar()

    def build_action_bar(self):
        action_bar = Gtk.ActionBar()
        self.builder.expose_object("actionbar", action_bar)
        self.window.layout.pack_end(action_bar, False, False, 0)

        apply_btn = Gtk.Button.new_from_stock(Gtk.STOCK_SAVE)
        apply_btn.connect("clicked", self.update_setting)
        apply_btn.get_style_context().add_class("suggested-action")
        action_bar.pack_end(apply_btn)

        cancel_btn = Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)
        cancel_btn.connect("clicked", self.reset)
        action_bar.pack_end(cancel_btn)

        action_bar.show_all()
        action_bar.hide()

    def on_allowance_toggled(self, widget, path):
        self.list_store[path][3] = not self.list_store[path][3]
        actionbar = self.builder.get_object("actionbar")
        actionbar.show()

    def field_changed(self, source, state=None):
        actionbar = self.builder.get_object("actionbar")
        actionbar.show()

    def build_form(self):
        switch = self.builder.get_object("has_laboratory")
        switch.set_active(self.setting.has_laboratory)
        switch = self.builder.get_object("has_telemedical")
        switch.set_active(self.setting.has_telemedical)
        switch = self.builder.get_object("default_end_of_month")
        switch.set_active(self.setting.default_end_of_month)

        entry = self.builder.get_object("first_aid_kit")
        entry.set_value(self.setting.first_aid_kit)
        entry = self.builder.get_object("rescue_bag")
        entry.set_value(self.setting.rescue_bag)

        entry = self.builder.get_object("expire_date_warning_delay")
        entry.set_value(self.setting.expire_date_warning_delay)

        self.builder.connect_signals({
            'on_field_changed': self.field_changed,
            'on_import_clicked': self.import_file
            })

    def build_allowance_tree(self):
        treeview = self.builder.get_object("allowance-treeview")
        self.update_model()

        text_renderer = Gtk.CellRendererText()
        checkbox_renderer = Gtk.CellRendererToggle()
        checkbox_renderer.connect("toggled", self.on_allowance_toggled)

        column = Gtk.TreeViewColumn(_("Name"), text_renderer, text=0)
        column.set_expand(True)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Version"), text_renderer, text=1)
        column.set_expand(True)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Author"), text_renderer, text=2)
        column.set_expand(True)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Active"), checkbox_renderer, active=3)
        treeview.append_column(column)

    def update_model(self):
        treeview = self.builder.get_object("allowance-treeview")

        self.list_store = Gtk.ListStore(str, str, str, bool, int)

        # Get allowance data
        allowance_list = Allowance.objects.exclude(id=0).order_by("name")

        for item in allowance_list:
            self.list_store.append((item.name, item.version, item.author, item.active, item.id))

        treeview.set_model(self.list_store)

        query_count_all()

    def get_active_allowance(self):
        treeview = self.builder.get_object("allowance-treeview")

        model = treeview.get_model()
        # log.debug(model)
        active_allowances = []
        for item in model:
            active = item[3]
            allowance_id = item[4]
            if active:
                active_allowances.append(allowance_id)

        return active_allowances

    def update_setting(self, source):
        active_allowances = self.get_active_allowance()

        # Bulk update allowances
        Allowance.objects.exclude(id=0).update(active=False)
        Allowance.objects.filter(id__in=active_allowances).update(active=True)

        fields = {
            "spinbutton": [
                "first_aid_kit",
                "rescue_bag",
                "expire_date_warning_delay",
            ],
            "switch": [
                "has_laboratory",
                "has_telemedical",
                "default_end_of_month"
            ]
        }

        cleaned_data = get_form_data(InventorySettingsForm, self.builder, fields)
        if cleaned_data is None:
            return

        # Show a dialog if the number of rescue bags is decreased in order to
        # select which one to delete
        if cleaned_data["rescue_bag"] < self.setting.rescue_bag:
            self.invalid = False
            self.dialog_delete(cleaned_data["rescue_bag"])
            if self.invalid:
                return

        for (key, value) in cleaned_data.items():
            setattr(self.setting, key, value)

        self.params.save()
        self.params.allowances = self.params.refresh_allowances()

        # Check for rescue bags
        if cleaned_data["rescue_bag"] > self.setting.rescue_bag:
            self.create_rescue_bags(cleaned_data["rescue_bag"])

        # Check for laboratory
        if cleaned_data["has_laboratory"]:
            obj, created = Location.objects.get_or_create(
                id=10,
                defaults={"name": "Laboratory", "id": 10}
            )
            if created:
                self.params.refresh_locations()

        # Check for telemedical
        if cleaned_data["has_telemedical"]:
            obj, created = Location.objects.get_or_create(
                id=20,
                defaults={"name": "Telemedical", "id": 20}
            )
            if created:
                self.params.refresh_locations()

        # Update the action menu
        self.application.lookup_action("laboratory").set_enabled(cleaned_data["has_laboratory"])
        self.application.lookup_action("telemedical").set_enabled(cleaned_data["has_telemedical"])

        query_count_all()

        self.reset()

    def create_rescue_bags(total):
        current = RescueBag.objects.count()
        missing = total - current
        if missing < 1:
            # Nothing to do
            log.debug("Number of RescueBag in database higher than needed")
            return True

        log.info("Missing some rescue bag instances. Creating...")
        for i in range(missing):
            location = Location.objects.create(
                name="Rescue Bag {0}".format(i),
                parent_id=0,
                is_rescue_bag=True
            )

            RescueBag.objects.create(
                name="Rescue Bag {0}".format(i),
                location_id=location.id
                )

            return True

    def reset(self, source=None):
        self.update_model()
        self.build_form()

        self.builder.get_object("actionbar").hide()

    def dialog_delete(self, total):
        # Check the real number of RescueBag instances to delete
        current = RescueBag.objects.count()
        count = current - total
        if count <= 0:
            log.debug("Number of RescueBag in database is high than requested.")
            return

        builder = get_builder("rescue_bag_dialog.ui")
        dialog = builder.get_object("dialog")

        # Set message (showing remaining rescue bags to select for deletion)
        # Adapt for plural form
        label = builder.get_object("label")
        btn = builder.get_object("btn-delete")
        if count < 2:
            msg_text = _("Select the rescue bag to delete.")
            btn.set_label(_("Delete this rescue bag"))
        else:
            msg_text = _("Select the {0} rescue bags to delete.")
            btn.set_label(_("Delete these rescue bags"))
        label.set_text(msg_text.format(count))

        # Create the Treeview
        self.build_rescue_bag_tree(builder, count)

        # Connect signals
        builder.connect_signals({
            "on-response": (self.response_delete, dialog, builder, count),
            "on-cancel": (self.dialog_destroy, dialog),
        })

        query_count_all()

        dialog.run()

        dialog.destroy()

    def dialog_destroy(self, source, dialog):
        """Destroy a Gtk.Dialog widget.

        `source`: event source widget. Not used.
        `dialog`: Gtk.Dialog widget to delete.

        Set `invalid` as True because the action was aborted by the user.
        """
        self.invalid = True
        dialog.destroy()

    def response_delete(self, source, dialog, builder, count):
        # Get selected RescueBag ID to delete
        to_delete = []
        for row in self.rescue_bag_store:
            if row[1]:
                to_delete.append(row[2])

        if len(to_delete) != count:
            return

        rescue_bags = RescueBag.objects.filter(id__in=to_delete).prefetch_related("location")

        for rescue_bag in rescue_bags:
            rescue_bag.location.delete()
            rescue_bag.delete()

        query_count_all()
        dialog.destroy()
        return True

    def build_rescue_bag_tree(self, builder, count):
        treeview = builder.get_object("treeview")
        self.update_rescue_bag_model(treeview)

        text_renderer = Gtk.CellRendererText()
        checkbox_renderer = Gtk.CellRendererToggle()
        checkbox_renderer.connect("toggled", self.on_rescue_bag_toggled, count)

        column = Gtk.TreeViewColumn(_("Name"), text_renderer, text=0)
        column.set_expand(True)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Delete"), checkbox_renderer, active=1)
        treeview.append_column(column)

    def on_rescue_bag_toggled(self, widget, path, count):
        # Check the count is not overtaken
        current_count = 0
        for item in self.rescue_bag_store:
            if item[1]:
                current_count += 1

        # Always allow deselect
        if self.rescue_bag_store[path][1]:
            self.rescue_bag_store[path][1] = False
            return

        # If count is obtain: do nothing
        if current_count == count:
            return

        self.rescue_bag_store[path][1] = True
        return

    def update_rescue_bag_model(self, treeview):
        self.rescue_bag_store = Gtk.ListStore(str, bool, int)

        # Get allowance data
        rescue_bag_list = RescueBag.objects.all().order_by("name")

        for item in rescue_bag_list:
            # Append to the ListStore
            self.rescue_bag_store.append((item.name, False, item.id))

        treeview.set_model(self.rescue_bag_store)
        treeview.show_all()

        query_count_all()

    def import_file(self, source):
        log.debug("Import")

        filechooser = self.builder.get_object("import-file")
        filename = filechooser.get_filename()

        button = self.builder.get_object("import-btn")
        label = self.builder.get_object("import-msg")

        # Reset label text
        label.set_text("")

        if not filename:
            label.set_markup(_("Please select a file."))
            return False

        # Set Spinner
        spinner = Gtk.Spinner()
        button.set_label("")
        button.set_image(spinner)
        button.set_sensitive(False)
        spinner.show()
        spinner.start()

        def thread_run():
            handler = Importer()

            res = handler.read_package(filename)
            if not res:
                label.set_text(handler.status)
                return False

            res = handler.check_signature()
            if not res:
                label.set_text(handler.status)
                return False

            res = handler.check_conformity()
            if not res:
                label.set_text(handler.status)
                return False

            res = handler.deploy()
            if not res:
                label.set_text(handler.status)
                return False

            label.set_text("Success")
            GLib.idle_add(cleanup, filename)

        def cleanup(result):
            spinner.stop()
            button.set_label(_("Import"))
            button.set_image(None)
            button.set_sensitive(True)

            self.update_model()
            t.join()

        t = threading.Thread(target=thread_run)
        t.start()

        return True
