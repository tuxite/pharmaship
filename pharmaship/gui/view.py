#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pharmaship Main GUI class."""
import datetime
import subprocess
import platform
import threading
import locale
import ctypes
import sys
import os

from pathlib import Path

import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk, Gio, Gdk, GLib

from django.utils.translation import gettext as _
from django.utils import translation
from django.conf import settings

from pharmaship.core.utils import log, end_of_month, add_months, get_content_types, query_count_all
from pharmaship.core.config import read_config, write_config

from pharmaship.gui import views, export, utils, widgets

from pharmaship.inventory import models
from pharmaship.inventory.utils import get_location_list
from pharmaship.inventory import search


# Constants
MED_OBS_SHT = "medical_observation_sheet.{0}.pdf"

# Language support
try:
    if hasattr(locale, 'bindtextdomain'):
        libintl = locale
    elif os.name == 'nt':
        libintl = ctypes.cdll.LoadLibrary('libintl-8.dll')
    elif sys.platform == 'darwin':
        libintl = ctypes.cdll.LoadLibrary('libintl.dylib')

    # setup the textdomain in gettext so Gtk3 can find it
    libintl.bindtextdomain("com.devmaretique.pharmaship", str(settings.PHARMASHIP_LOCALE))
    libintl.textdomain("com.devmaretique.pharmaship")

except (OSError, AttributeError) as error:
    # disable translations altogether for consistency
    log.exception("Impossible to set translation for Pharmaship. %s", error)
    translation.activate('en_US.UTF-8')


def set_langage(lang_code: str):
    """Application wide language switcher.

    Set Django Translation (gettext) and C library `locale` for Glade/Gtk
    files.

    :param: lang_code: (string) language code
    """
    locale_str = None

    if platform.system() == "Windows":
        if lang_code == "fr":
            locale_str = "french"
        else:
            locale_str = "english"
    else:
        locale_str = (lang_code, "utf8")

    try:
        locale.setlocale(locale.LC_ALL, locale_str)
    except locale.Error:
        log.exception("Locale (%s) non installed on the operating system. Switching to 'C' locale.", locale_str)
        locale.setlocale(locale.LC_ALL, 'C')
        translation.activate('en')
        return None

    # Activate Django translation language
    translation.activate(lang_code)

    return None


class GlobalParameters:
    """Global parameters for Pharmaship application and views."""

    def __init__(self):
        self.config = read_config()

        self.allowances = models.Allowance.objects.filter(active=True)
        self.today = end_of_month(datetime.date.today())
        self.content_types = get_content_types()
        self.locations = []

        self.vessel = self.config.vessel
        self.setting = self.config.inventory
        self.application = self.config.application
        self.pluralizer = utils.get_pluralizer()

        self.refresh_locations()

    def refresh_locations(self):
        """Refresh Location instances list."""
        self.locations = get_location_list()
        return self.locations

    def refresh_setting(self):
        self.config = read_config()
        self.setting = self.config.inventory
        return self.setting

    def refresh_allowances(self):
        self.allowances = models.Allowance.objects.filter(active=True)
        return self.allowances

    def refresh_vessel(self):
        self.config = read_config()
        self.vessel = self.config.vessel
        return self.vessel

    def refresh(self):
        self.config = read_config()
        self.content_types = get_content_types()
        self.locations = get_location_list()
        self.allowances = models.Allowance.objects.filter(active=True)
        self.vessel = self.config.vessel
        self.setting = self.config.inventory
        self.application = self.config.application

    def save(self):
        """Save current configuration into file."""
        res = write_config(self.config)
        if not res:
            log.error("Configuration non updated.")


class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, params, actions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions = actions
        self.params = params

        # Set the window title
        self.set_wmclass("Pharmaship", "Pharmaship")
        self.set_title("Pharmaship")
        icon = utils.get_image("pharmaship_icon.svg").get_pixbuf()
        self.set_icon(icon)

        # Set default mode
        self.mode = "dashboard"

        # Set default refresh view action (dummy function)
        self.refresh_view = lambda: None

        self.builder = Gtk.Builder()
        self.builder.set_translation_domain("com.devmaretique.pharmaship")

        self.layout = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.add(self.layout)

        # Temporary image
        image = utils.get_image("home.png")
        self.layout.pack_start(image, True, True, 0)

        self.build_header_bar()

    def build_header_bar(self):
        # Header bar
        hb = Gtk.HeaderBar()
        self.builder.expose_object("header-bar", hb)

        hb.set_show_close_button(True)
        # hb.props.title = "Pharmaship"
        hb.set_title("Pharmaship")
        self.set_titlebar(hb)
        self.set_title("Pharmaship")

        # Menu button
        builder = utils.get_builder('menu/settings.xml')
        menu = builder.get_object("app-menu")

        button = widgets.ButtonWithImage("open-menu-symbolic.svg", btn_class=Gtk.MenuButton)
        popover = Gtk.Popover.new_from_model(button, menu)
        button.set_popover(popover)
        hb.pack_end(button)

        # Search bar
        self.searchbar = Gtk.SearchEntry()
        self.searchbar.set_placeholder_text(_("Search something..."))
        self.searchbar.connect("activate", self.on_search)
        self.searchbar.props.width_request = 300
        hb.pack_end(self.searchbar)

        # Mode button
        builder = utils.get_builder("menu/modes.xml")
        menu = builder.get_object("app-menu")

        self.mode_button = Gtk.MenuButton(self.mode)
        popover = Gtk.Popover.new_from_model(self.mode_button, menu)
        self.mode_button.set_popover(popover)
        self.mode_button.props.width_request = 120
        self.mode_button.get_style_context().add_class("suggested-action")
        hb.pack_start(self.mode_button)

        # Save button
        button = widgets.ButtonWithImage("document-save-as-symbolic.svg", tooltip=_("Export as PDF"), action="app.save")
        hb.pack_start(button)
        self.builder.expose_object("hb-btn-save", button)

        # Create hb date check button
        self.create_hb_date_button()
        self.expiry_date_button_label()

    def on_search(self, source):
        search_text = source.get_text().strip()
        if len(search_text) < 2:
            return False
        search_result = search.search(search_text, self.params)

        # Create a Popover with ListBox
        main_builder = utils.get_builder("search_popover.ui")
        popover = main_builder.get_object("popover")
        popover.set_relative_to(self.searchbar)
        popover.get_style_context().add_class("popover-search")
        popover.props.width_request = self.searchbar.props.width_request

        listbox = main_builder.get_object("listbox")

        if len(search_result) == 0:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(_("No result found. Try again!"))
            row.add(label)
            listbox.add(row)
            listbox.set_selection_mode(0)
            popover.show_all()
            scrolled = main_builder.get_object("scrolled")
            scrolled.set_min_content_height(-1)
            scrolled.set_max_content_height(-1)
            return True

        for item in search_result:
            builder = utils.get_builder("search_listboxrow.ui")
            row = Gtk.ListBoxRow()
            box = builder.get_object("box")
            row.add(box)
            listbox.add(row)
            parent_name = builder.get_object("parent_name")
            parent_name_text = "<b>{0}</b> ({1})".format(item["parent_name"], item["details"])
            parent_name.set_markup(parent_name_text)
            other_names = builder.get_object("other_names")
            if item["other_names"]:
                other_names_text = ", ".join(item["other_names"])
                other_names.set_text(_("Other names: {0}").format(other_names_text))
            else:
                other_names.destroy()
            locations = builder.get_object("locations")
            if item["locations"]:
                locations_text = ", ".join(item["locations"])
                locations.set_text(_("Locations: {0}").format(locations_text))
            else:
                locations.destroy()

            quantity_text = "<b>{0}<small>/{1}</small></b>".format(item["quantity"], item["required"])
            quantity = builder.get_object("quantity")
            quantity.set_markup(quantity_text)

            group = builder.get_object("group")
            group.set_text(item["group"])

            # Type
            box = builder.get_object("type-box")
            for item_type in item["type"]:
                btn = Gtk.LinkButton("", item_type["label"])
                # Remove the "pseudo" tooltip showing nothing but existing...
                btn.set_tooltip_text(None)
                btn.connect("activate-link", self.search_click, item, item_type["name"])
                box.pack_start(btn, True, True, 0)

        popover.show_all()

    def search_click(self, source, item, item_type):
        """Open the related view of the item clicked."""
        if item_type not in self.actions.list_actions():
            log.warning("Action %s not registered.", item_type)
            return False

        self.actions.activate_action(item_type, GLib.Variant("i", item["id"]))

    # Expiry date check management
    def create_hb_date_button(self):
        # Update the HeaderBar
        hb = self.builder.get_object("header-bar")

        self.hb_btn = self.builder.get_object("header-bar-btn")
        if self.hb_btn is None:
            self.hb_btn = Gtk.Button()
            self.hb_btn.set_relief(Gtk.ReliefStyle.NONE)
            self.hb_btn.connect("clicked", self.expiry_date_dialog)
            self.builder.expose_object("header-bar-btn", self.hb_btn)
            hb.pack_start(self.hb_btn)

        self.popover = Gtk.Popover()
        self.popover.set_position(Gtk.PositionType.BOTTOM)
        self.popover.set_relative_to(self.hb_btn)
        self.popover.get_style_context().add_class("popover-calendar")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_spacing(10)
        self.popover.add(box)

        label = Gtk.Label(_("Double-click on expiry date"))
        box.pack_start(label, True, True, 0)

        calendar = Gtk.Calendar()
        # calendar.set_display_options(Gtk.CalendarDisplayOptions(43))
        calendar.set_property("show-heading", True)
        calendar.set_property("show-week-numbers", True)
        calendar.set_property("show-day-names", True)
        calendar.get_style_context().add_class("calendar")
        calendar.connect("day-selected-double-click", self.expiry_date_changed)
        box.pack_start(calendar, True, True, 0)

        linked_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        linked_btn.get_style_context().add_class("linked")
        box.pack_start(linked_btn, True, True, 0)

        btn = Gtk.Button(_("End of month"))
        btn.connect("clicked", self.update_today, 0)
        linked_btn.pack_start(btn, True, True, 0)

        btn = Gtk.Button(_("T + 2 months"))
        btn.connect("clicked", self.update_today, 2)
        linked_btn.pack_start(btn, True, True, 0)

        btn = Gtk.Button(_("T + 4 months"))
        btn.connect("clicked", self.update_today, 4)
        linked_btn.pack_start(btn, True, True, 0)
        # hb.set_custom_title(hb_btn)
        hb.show_all()

    def update_today(self, source, month_delta):
        today = datetime.date.today()
        tmp_date = add_months(today, month_delta)

        self.params.today = end_of_month(tmp_date)
        self.expiry_date_button_label()

        self.popover.popdown()

        self.refresh_view()

    def expiry_date_button_label(self):
        expiry_text = _("Expiry up to: {0}").format(self.params.today.strftime("%d/%m/%Y"))
        self.hb_btn.set_label(expiry_text)

    def expiry_date_dialog(self, source):
        self.popover.show_all()
        self.popover.popup()

    def expiry_date_changed(self, source):
        date = source.get_date()

        self.popover.popdown()

        self.params.today = datetime.date(
            year=date.year,
            month=date.month+1,
            day=date.day
            )

        self.expiry_date_button_label()
        self.refresh_view()


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.devmaretique.pharmaship", **kwargs)
        self.window = None

        self.params = GlobalParameters()
        self.setting = self.params.setting

        resource = Gio.resource_load(str(settings.PHARMASHIP_GUI / 'resources.gresource'))
        Gio.Resource._register(resource)

    def set_mode(self, mode):
        modes = {
            "dashboard": self.on_dashboard,
            "medicines": self.on_medicines,
            "equipment": self.on_equipment,
            "first_aid_kits": self.on_first_aid_kits,
            "rescue_bag": self.on_rescue_bag,
            "laboratory": self.on_laboratory,
            "telemedical": self.on_telemedical,
            "locations": self.on_location_manager,
            "allowances": self.on_allowance_manager,
            "settings": self.on_vessel_settings
        }

        modes[mode](None, None)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("dashboard", None)
        action.connect("activate", self.on_dashboard)
        self.add_action(action)

        action = Gio.SimpleAction.new("medicines", GLib.VariantType.new("i"))
        action.connect("activate", self.on_medicines)
        self.add_action(action)

        action = Gio.SimpleAction.new("equipment", GLib.VariantType.new("i"))
        action.connect("activate", self.on_equipment)
        self.add_action(action)

        action = Gio.SimpleAction.new("first_aid_kits", None)
        action.connect("activate", self.on_first_aid_kits)
        self.add_action(action)

        action = Gio.SimpleAction.new("rescue_bags", None)
        action.connect("activate", self.on_rescue_bag)
        self.add_action(action)

        action = Gio.SimpleAction.new("laboratory", GLib.VariantType.new("i"))
        action.connect("activate", self.on_laboratory)
        action.set_enabled(False)
        self.add_action(action)
        if self.setting.has_laboratory:
            action.set_enabled(True)

        action = Gio.SimpleAction.new("telemedical", GLib.VariantType.new("i"))
        action.connect("activate", self.on_telemedical)
        action.set_enabled(False)
        self.add_action(action)
        if self.setting.has_telemedical:
            action.set_enabled(True)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("save", None)
        action.connect("activate", self.on_save)
        self.add_action(action)

        action = Gio.SimpleAction.new("vessel_settings", None)
        action.connect("activate", self.on_vessel_settings)
        self.add_action(action)

        action = Gio.SimpleAction.new("location_manager", None)
        action.connect("activate", self.on_location_manager)
        self.add_action(action)

        action = Gio.SimpleAction.new("allowance_manager", None)
        action.connect("activate", self.on_allowance_manager)
        self.add_action(action)

        action = Gio.SimpleAction.new_stateful(
            "language",
            GLib.VariantType.new('s'),
            GLib.Variant.new_string(self.params.application.lang)
            )
        action.connect("activate", self.on_language)
        self.add_action(action)

        set_langage(self.params.application.lang)

        action = Gio.SimpleAction.new("db_export", None)
        action.connect("activate", self.db_export)
        self.add_action(action)

        action = Gio.SimpleAction.new("db_import", None)
        action.connect("activate", self.db_import)
        self.add_action(action)

        action = Gio.SimpleAction.new("open_log", None)
        action.connect("activate", self.open_log)
        self.add_action(action)

        action = Gio.SimpleAction.new("open_config", None)
        action.connect("activate", self.open_config)
        self.add_action(action)

        action = Gio.SimpleAction.new("contact_ccmm", None)
        action.connect("activate", self.contact_ccmm)
        self.add_action(action)

        action = Gio.SimpleAction.new("medical_obs", None)
        action.connect("activate", self.medical_obs)
        self.add_action(action)

        if settings.PHARMASHIP_USER_MANUAL.exists():
            action = Gio.SimpleAction.new("doc", None)
            action.connect("activate", self.open_doc)
            self.add_action(action)

        action = Gio.SimpleAction.new("med_guide", None)
        action.connect("activate", self.medical_guide)
        self.add_action(action)

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = AppWindow(application=self, params=self.params, actions=self)
            self.window.set_size_request(800, 600)

        self.on_dashboard(None, None)
        self.window.show_all()

        query_count_all()
        log.info("Initialization completed!")

    def on_about(self, action, param):
        builder = utils.get_builder("about_dialog.ui")
        about_dialog = builder.get_object("about-dialog")
        # Set version
        about_dialog.set_version(settings.PHARMASHIP_VERSION)
        about_dialog.set_transient_for(self.window)
        about_dialog.present()

    def on_quit(self, action, param):
        self.quit()

    def on_language(self, action, param):
        log.info("Lang changed: %s", param)
        action.set_state(param)
        self.params.application.lang = param.get_string()
        self.params.save()

        set_langage(self.params.application.lang)

        # Get window parameters
        window_size = self.window.get_size()
        # Position is not reliable on Wayland
        window_position = self.window.get_position()
        mode = self.window.mode

        self.window.destroy()
        self.window = AppWindow(application=self, params=self.params, actions=self)
        self.window.set_size_request(800, 600)

        self.set_mode(mode)
        self.window.set_default_size(*window_size)

        self.window.move(
            x=window_position[0],
            y=window_position[1]
        )

        self.window.show_all()

    def clear_layout(self):
        # Remove old content
        self.window.layout.destroy()
        # Re-create an empty box
        self.window.layout = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.window.add(self.window.layout)

        self.window.refresh_view = lambda: None

        return True

    def on_dashboard(self, action, param):
        log.info("Dashboard!")
        self.window.mode = "dashboard"
        self.window.mode_button.set_label(_("Dashboard"))

        self.clear_layout()

        view = views.dashboard.View(self.window)
        view.create_main_layout()

        # Set headbar button action
        self.window.refresh_view = view.refresh_dashboard

    def on_location_manager(self, action, param):
        self.window.mode = "locations"
        self.window.mode_button.set_label(_("Location Manager"))

        self.clear_layout()

        view = views.location_manager.View(self.window)
        view.create_main_layout()

    def on_vessel_settings(self, action, param):
        self.window.mode = "settings"
        self.window.mode_button.set_label(_("Settings"))

        self.clear_layout()

        view = views.vessel_settings.View(self.window)
        view.create_main_layout()

    def on_allowance_manager(self, action, param):
        self.window.mode = "allowances"
        self.window.mode_button.set_label(_("Allowance Manager"))

        self.clear_layout()

        view = views.allowance_manager.View(self.window, self)
        view.create_main_layout()

    def on_medicines(self, action, param):
        self.window.mode = "medicines"
        self.window.mode_button.set_label(_("Medicines"))

        self.clear_layout()

        chosen = None
        if type(param) is GLib.Variant:
            chosen = param.get_int32()

        view = views.medicines.View(self.window, chosen)
        view.create_main_layout()

        # Set headbar button action
        self.window.refresh_view = view.refresh_grid

    def on_equipment(self, action, param):
        self.window.mode = "equipment"
        self.window.mode_button.set_label(_("Equipment"))

        self.clear_layout()

        chosen = None
        if type(param) is GLib.Variant:
            chosen = param.get_int32()

        view = views.equipment.View(self.window, chosen)
        view.create_main_layout()

        # Set headbar button action
        self.window.refresh_view = view.refresh_grid

        self.window.layout.show_all()

    def on_first_aid_kits(self, action, param):
        self.window.mode = "first_aid_kits"
        self.window.mode_button.set_label(_("First Aid Kits"))

        self.clear_layout()

        view = views.first_aid_kits.View(self.window)
        view.create_main_layout()

        # Set headbar button action
        self.window.refresh_view = view.refresh_grid

    def on_rescue_bag(self, action, param):
        self.window.mode = "rescue_bag"
        self.window.mode_button.set_label(_("Rescue Bags"))

        self.clear_layout()

        view = views.rescue_bag.View(self.window)
        view.create_main_layout()

        # Set headbar button action
        self.window.refresh_view = view.refresh_grid

    def on_laboratory(self, action, param):
        self.window.mode = "laboratory"
        self.window.mode_button.set_label(_("Laboratory"))

        self.clear_layout()

        chosen = None
        if type(param) is GLib.Variant:
            chosen = param.get_int32()

        view = views.laboratory.View(self.window, chosen)
        view.create_main_layout()

        # Set headbar button action
        self.window.refresh_view = view.refresh_grid

        self.window.layout.show_all()

    def on_telemedical(self, action, param):
        self.window.mode = "telemedical"
        self.window.mode_button.set_label(_("Telemedical"))

        self.clear_layout()

        chosen = None
        if type(param) is GLib.Variant:
            chosen = param.get_int32()

        view = views.telemedical.View(self.window, chosen)
        view.create_main_layout()

        # Set headbar button action
        self.window.refresh_view = view.refresh_grid

        self.window.layout.show_all()

    def db_export(self, action, param):
        cls = views.developers.DatabaseExport(self.window)
        cls.show_dialog()

    def db_import(self, action, param):
        cls = views.developers.DatabaseImport(self.window)
        cls.show_dialog()

    def open_log(self, action, param):
        self.open_file(settings.PHARMASHIP_LOG)

    def open_config(self, action, param):
        """Open the configuration YAML file."""
        self.open_file(settings.PHARMASHIP_CONF)

    def open_doc(self, action, param):
        """Open the user manual."""
        self.open_file(settings.PHARMASHIP_USER_MANUAL)

    def on_save(self, action, param):
        # Get the adequate class
        if self.window.mode == "medicines":
            cls = export.medicines.Export(self.window.params)
        elif self.window.mode == "equipment":
            cls = export.equipment.Export(self.window.params)
        elif self.window.mode == "telemedical":
            cls = export.telemedical.Export(self.window.params)
        elif self.window.mode == "laboratory":
            cls = export.laboratory.Export(self.window.params)
        elif self.window.mode == "rescue_bag":
            cls = export.rescue_bag.Export(self.window.params)
        elif self.window.mode == "first_aid_kits":
            cls = export.first_aid_kits.Export(self.window.params)
        else:
            cls = export.dashboard.Export(self.window.params)

        # Get the button
        button = self.window.builder.get_object("hb-btn-save")

        spinner = Gtk.Spinner()
        button.set_image(spinner)
        button.set_sensitive(False)
        spinner.start()

        def thread_run():
            # Call the class method to generate a temporary PDF file
            pdf_filename = cls.pdf_print()
            GLib.idle_add(cleanup, pdf_filename)

        def cleanup(result):
            spinner.stop()
            image = utils.get_icon("document-save-as-symbolic.svg")
            button.set_image(image)
            button.set_sensitive(True)
            t.join()
            self.open_file(result)

        t = threading.Thread(target=thread_run)
        t.start()

    def open_file(self, filename):
        # Open the pdf file using the platform default program
        if filename:
            if platform.system() == 'Darwin':
                subprocess.call(('open', filename))
            elif platform.system() == 'Windows':
                os.startfile(filename)
            else:
                subprocess.call(('xdg-open', filename))

    def contact_ccmm(self, action, param):
        """Open the system mail client to email the French TMAS."""
        tmas_mail = "ccmm@chu-toulouse.fr"
        self.open_file("mailto:{0}".format(tmas_mail))

    def medical_obs(self, action, param):
        """Open if available the medical observation sheet PDF."""
        _name = MED_OBS_SHT.format(self.params.application.lang)
        fileobj = Path(settings.PHARMASHIP_DATA / _name)
        if fileobj.exists():
            self.open_file(fileobj)
        else:
            # Fallback
            log.warning("Med. observation sheet not available for this lang.")
            _name = MED_OBS_SHT.format("fr")
            fileobj = Path(settings.PHARMASHIP_DATA / _name)
            self.open_file(fileobj)

    def medical_guide(self, action, param):
        """Open the International medical guide for ships."""
        _name = "9789240682313_eng.pdf"
        fileobj = Path(settings.PHARMASHIP_DATA / _name)
        if fileobj.exists():
            self.open_file(fileobj)

    def gtk_style(self):
        """Add CSS styles to the application."""
        style_provider = Gtk.CssProvider()

        style_provider.load_from_resource("/com/devmaretique/pharmaship/style.css")
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

if __name__ == '__main__':
    app = Application()
    app.gtk_style()

    app.run()
