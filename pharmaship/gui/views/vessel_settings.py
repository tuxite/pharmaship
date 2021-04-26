# -*- coding: utf-8 -*-
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk

from django.utils.translation import gettext as _

from pharmaship.core.utils import log

from pharmaship.settings.forms import VesselSettingsForm

from pharmaship.gui import utils


class View:
    def __init__(self, window):
        self.window = window
        self.params = window.params
        self.vessel = self.params.vessel
        self.builder = utils.get_builder("vessel_settings.ui")

    def create_main_layout(self):
        # Create content
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.props.hscrollbar_policy = Gtk.PolicyType.NEVER
        # No overlay of the scrollbar
        self.scrolled.props.overlay_scrolling = False
        self.window.layout.pack_start(self.scrolled, True, True, 0)

        self.build_form()

        self.window.layout.show_all()

        self.build_action_bar()

    def build_action_bar(self):
        action_bar = Gtk.ActionBar()
        self.builder.expose_object("actionbar", action_bar)
        self.window.layout.pack_end(action_bar, False, False, 0)

        apply_btn = Gtk.Button.new_from_stock(Gtk.STOCK_SAVE)
        apply_btn.connect("clicked", self.update_vessel)
        apply_btn.get_style_context().add_class("suggested-action")
        action_bar.pack_end(apply_btn)

        cancel_btn = Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)
        cancel_btn.connect("clicked", self.reset)
        action_bar.pack_end(cancel_btn)

        action_bar.show_all()
        action_bar.hide()

    def build_form(self):
        box = self.builder.get_object("settings-box")
        self.scrolled.add(box)

        self.set_values()

        self.builder.connect_signals({'on_field_changed': self.field_changed})

    def set_values(self):
        if self.vessel is None:
            return

        entry = self.builder.get_object("name")
        entry.set_text(self.vessel.name)

        entry = self.builder.get_object("imo")
        entry.set_text(str(self.vessel.imo))
        entry = self.builder.get_object("mmsi")
        entry.set_text(str(self.vessel.mmsi))
        entry = self.builder.get_object("call_sign")
        entry.set_text(self.vessel.call_sign)
        entry = self.builder.get_object("flag")
        entry.set_text(self.vessel.flag)
        entry = self.builder.get_object("port_of_registry")
        entry.set_text(self.vessel.port_of_registry)

        entry = self.builder.get_object("sat_phone")
        entry.set_text(self.vessel.sat_phone)
        entry = self.builder.get_object("gsm_phone")
        entry.set_text(self.vessel.gsm_phone)
        entry = self.builder.get_object("email")
        entry.set_text(self.vessel.email)

        entry = self.builder.get_object("shipowner")
        entry.set_text(self.vessel.shipowner)
        entry = self.builder.get_object("address_buffer")
        entry.set_text(self.vessel.address)

        entry = self.builder.get_object("address")
        entry.set_border_width(1)

    def field_changed(self, source):
        self.builder.get_object("actionbar").show()

    def reset(self, source):
        log.debug("Reload vessel data and re-build the view.")
        for child in self.scrolled.get_children():
            child.destroy()

        self.build_form()
        self.builder.get_object("actionbar").hide()

    def update_vessel(self, source):
        fields = {
            "entry": [
                "name",
                "imo",
                "mmsi",
                "call_sign",
                "flag",
                "port_of_registry",
                "sat_phone",
                "gsm_phone",
                "email",
                "shipowner",
            ],
            "textview": [
                "address"
            ]
        }

        cleaned_data = utils.get_form_data(VesselSettingsForm, self.builder, fields)
        if cleaned_data is None:
            return

        for (key, value) in cleaned_data.items():
            setattr(self.vessel, key, value)
        self.params.save()

        self.params.refresh_vessel()

        self.builder.get_object("actionbar").hide()
