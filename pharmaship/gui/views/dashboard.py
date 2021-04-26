# -*- coding: utf-8 -*-
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk, Gdk, Pango, GLib

import tempfile
import csv
import json
import datetime
import threading

from django.utils.translation import gettext as _

from pharmaship.core.utils import log, query_count_all

from pharmaship.gui import utils

import pharmaship.inventory.parsers as parsers
from pharmaship.gui.export.dashboard import Export, ExportMissing, ExportPerished
from pharmaship.gui.plots import dispatch


SECTIONS = {
    "molecules": _("molecules"),
    "equipment": _("equipment"),
    "laboratory": _("laboratory equipment"),
    "telemedical": _("telemedical equipment"),
    "first_aid_kit": _("first aid kits items"),
    "rescue_bag": _("rescue bags items")
}

TYPES = {
    "missing": _("Missing"),
    "perished": _("Perished"),
    "warning": _("Near expiry"),
    "nc": _("Non-conform")
}

WIDGETS = [
    "name",
    "btn",
    "label"
]

HEADERS = {
    "txt": {
        "medicines": {
            "missing": [_("Name (Dosage Form - Composition)"), _("Current/Required quantity"), _("Missing quantity")],
            "dated": [_("Name [INN] (Dosage Form - Composition)"), _("Quantity"), _("Expiry")],
            "nc": [_("Name [INN] (Dosage Form - Composition)"), _("Quantity"), _("Non-conformity")]
        },
        "articles": {
            "missing": [_("Name (Packaging)"), _("Current/Required quantity"), _("Missing quantity")],
            "dated": [_("Name [Equipment] (Packaging)"), _("Quantity"), _("Expiry")],
            "nc": [_("Name [Equipment] (Packaging)"), _("Quantity"), _("Non-conformity")],
        },
        "mixed": {
            "missing": [_("Name (Details)"), _("Current/Required quantity"), _("Missing quantity")],
            "dated": [_("Name [Parent]"), _("Quantity"), _("Expiry")],
            "nc": [_("Name [Parent]"), _("Quantity"), _("Non-conformity")],
        },
    },
    "csv": {
        "medicines": {
            "missing": ["name", "dosage_form", "composition", "current_quantity", "required_quantity", "missing_quantity"],
            "dated": ["name", "dosage_form", "composition", "inn", "quantity", "expiry"],
            "nc": ["name", "dosage_form", "composition", "inn", "quantity", "nc"]
        },
        "articles": {
            "missing": ["name", "packaging", "current_quantity", "required_quantity", "missing_quantity"],
            "dated": ["name", "packaging", "equipment", "quantity", "expiry"],
            "nc": ["name", "packaging", "equipment", "quantity", "nc"]
        },
        "mixed": {
            "missing": ["name", "current_quantity", "required_quantity", "missing_quantity"],
            "dated": ["name", "parent", "quantity", "expiry"],
            "nc": ["name", "parent", "quantity", "nc"]
        }
    }
}


def get_header(output, section, type):
    """Return header for CSV or text output details."""
    if output == "txt":
        res = HEADERS["txt"]
    else:
        res = HEADERS["csv"]

    if section == "molecules":
        res = res["medicines"]
    elif section in ["equipment", "laboratory", "telemedical"]:
        res = res["articles"]
    else:
        res = res["mixed"]

    if type == "missing":
        return res["missing"]
    elif type in ["perished", "warning"]:
        return res["dated"]
    elif type == "nc":
        return res["nc"]

    return []


def format_expiry(date):
    """Return formatted expiry date with in/ago sentence for detailled views."""
    today = datetime.date.today()
    near = _("in {0} days")
    expired = _("{0} days ago")

    diff = date - today
    days = diff.days

    if days > 0:
        add_str = near.format(days)
    else:
        add_str = expired.format(-days)

    result = "{0} ({1})".format(date.strftime("%Y-%m-%d"), add_str)
    return result


def format_nc(nc):
    result = []
    if nc["packaging"]:
        result.append("{0} {1}".format(_("Non-compliant packaging:"), nc["packaging"]))
    if nc["composition"]:
        result.append("{0} {1}".format(_("Non-compliant composition:"), nc["composition"]))
    if nc["molecule"]:
        result.append("{0} {1}".format(_("Non-compliant molecule:"), nc["molecule"]))
    return ", ".join(result)


def get_data_items(data):
    """Return formatted dictionary for use in dashboard and plots."""
    result = {
        "missing": [],
        "perished": [],
        "warning": [],
        "nc": [],
        "in_range": 0,
        "total": 0,
        "exp_dates": [],
    }

    for group in data:
        for element in data[group]:
            # result["total"] += 1
            result["exp_dates"] += element["exp_dates"]

            flag = False

            if element["has_nc"]:
                result["nc"].append(element)
                flag = True

            if element["required_quantity"] > element["quantity"]:
                result["missing"].append(element)
                flag = True

            if element["has_date_expired"]:
                result["perished"].append(element)
                continue
            if element["has_date_warning"]:
                result["warning"].append(element)
                continue

            if flag is False:
                result["in_range"] += 1

    result["total"] = result["in_range"]
    result["total"] += len(result["nc"])
    result["total"] += len(result["missing"])
    result["total"] += len(result["perished"])
    result["total"] += len(result["warning"])

    return result


class DataParser:
    def __init__(self, elements, section, type, params):
        self.type = type
        self.section = section
        self.params = params
        self.today = params.today
        self.warning = self.today + datetime.timedelta(days=params.setting.expire_date_warning_delay)

        self.elements = elements

    def contents(self, element):
        """Return `element` contents list."""
        if "medicines" in element:
            return element["medicines"]
        elif "articles" in element:
            return element["articles"]
        elif "contents" in element:
            return element["contents"]

        log.warning("Content not identified. Skipping. See debug log.")
        log.debug(element)
        return []

    def get_info(self, element):
        """Return specific `element` information according to `section`."""
        res = {
        }
        if self.section == "molecules":
            res["dosage_form"] = element["dosage_form"]
            res["composition"] = element["composition"]
            res["full_detail"] = "({0} - {1})".format(res["dosage_form"], res["composition"])
        elif self.section in ["equipment", "telemedical", "laboratory"]:
            res["packaging"] = element["packaging"]
            res["full_detail"] = "({0})".format(res["packaging"])
        else:
            res["full_detail"] = ""
        return res

    def get_name(self, element, item=None):
        """Return `element` name with `item` name if specified."""
        res = self.get_info(element)
        if item is None:
            res["name"] = element["name"]
        else:
            res["name"] = item["name"]
            res["parent"] = element["name"]

        if item and item["name"] != element["name"]:
            res["full_name"] = "{0} [{2}] {1}".format(res["name"], res["full_detail"], res["parent"])
        else:
            res["full_name"] = "{0} {1}".format(res["name"], res["full_detail"])

        return res

    def get_items(self):
        if self.type == "missing":
            return self.missing()
        elif self.type == "nc":
            return self.nc()
        elif self.type in ["perished", "warning"]:
            return self.dated()
        else:
            return []

    def get_nc(self, item):
        result = {
            "packaging": "",
            "molecule": "",
            "composition": ""
        }
        if "nc" in item and item["nc"]:
            if isinstance(item["nc"], str):
                nc_obj = json.loads(item["nc"])
            else:
                nc_obj = item["nc"]
            result = {**result, **nc_obj}
        if "nc_composition" in item:
            result["composition"] = item["nc_composition"]
        if "nc_molecule" in item:
            result["molecule"] = item["nc_molecule"]
        if "nc_packaging" in item:
            result["packaging"] = item["nc_packaging"]

        return result

    def missing(self):
        res = []
        for element in self.elements:
            element_dict = self.get_name(element)
            element_dict["current_quantity"] = element["quantity"]
            element_dict["required_quantity"] = element["required_quantity"]
            element_dict["missing_quantity"] = element_dict["required_quantity"] - element_dict["current_quantity"]
            res.append(element_dict)
        return res

    def nc(self):
        res = []
        for element in self.elements:
            for item in self.contents(element):
                nc = self.get_nc(item)

                if not any(nc.values()):
                    continue

                item_dict = self.get_name(element, item)
                item_dict["quantity"] = item["quantity"]
                item_dict["nc"] = nc
                item_dict["full_nc"] = format_nc(nc)

                res.append(item_dict)
        return res

    def dated(self):
        if self.type == "perished":
            check_date = self.today
        else:
            check_date = self.warning

        res = []
        for element in self.elements:
            for item in self.contents(element):
                if item["exp_date"] <= check_date:
                    item_dict = self.get_name(element, item)
                    item_dict["quantity"] = item["quantity"]
                    item_dict["exp_date"] = item["exp_date"]
                    item_dict["full_date"] = format_expiry(item["exp_date"])
                    res.append(item_dict)

        return res


class View:
    def __init__(self, window):
        self.window = window
        self.params = window.params
        self.vessel = self.params.vessel
        self.builder = utils.get_builder("dashboard.ui")

        self.warning_date = self.params.today + datetime.timedelta(days=self.params.setting.expire_date_warning_delay)

        self.data = {}

    def set_layout(self, refresh=False):
        self.get_molecules()
        self.get_equipment()
        self.get_rescue_bag()
        self.get_first_aid_kit()

        widget = self.builder.get_object("laboratory-box-child")
        if self.params.setting.has_laboratory:
            self.get_laboratory()
            widget.show_all()
        else:
            widget.hide()

        widget = self.builder.get_object("telemedical-box-child")
        if self.params.setting.has_telemedical:
            self.get_telemedical()
            widget.show_all()
        else:
            widget.hide()

        # Set values in the different widgets
        self.set_values(refresh=refresh)

        # Add visual daashboards
        self.graphic_condition()

    def create_main_layout(self):
        """Create the main layout for Dashboard view."""
        # Create content
        box = self.builder.get_object("box")
        self.window.layout.pack_start(box, True, True, 0)
        self.window.layout.show_all()

        self.set_layout()

        self.builder.connect_signals({
            "on-export-inventories": (self.export_all, "inventory"),
            "on-export-missing": (self.export_all, "missing"),
            "on-export-perished": (self.export_all, "perished"),
        })

    def refresh_dashboard(self):
        """Refresh the dashboard data."""
        # Remove the old graphics
        graphicbox = self.builder.get_object("graphics")
        for child in graphicbox.get_children():
            # Double remove/destroy... to be sure!
            # It seems matplotlib FigureCanvas is not destroyable?!
            graphicbox.remove(child)
            child.destroy()
        # Recall the main function
        self.set_layout(refresh=True)

    def export_all(self, source, type):
        export_function = None

        if type == "inventory":
            cls = Export(self.params)
            export_function = cls.pdf_print
        elif type == "missing":
            cls = ExportMissing(self.params, self.data)
            export_function = cls.pdf_print
        elif type == "perished":
            cls = ExportPerished(self.params, self.data)
            export_function = cls.pdf_print

        if export_function is None:
            return False

        # Get the button
        button = source

        spinner = Gtk.Spinner()
        button.set_image(spinner)
        button.set_sensitive(False)
        button.set_always_show_image(True)
        spinner.start()

        def thread_run():
            # Call the class method to generate a temporary PDF file
            pdf_filename = export_function()
            GLib.idle_add(cleanup, pdf_filename)

        def cleanup(result):
            spinner.stop()
            button.set_sensitive(True)
            button.set_always_show_image(False)
            t.join()
            utils.open_file(result)

        t = threading.Thread(target=thread_run)
        t.start()

    def set_values(self, refresh=False):
        objects = []
        import itertools
        for item in itertools.product(SECTIONS.keys(), TYPES.keys(), WIDGETS):
            identifier = "-".join(item)
            obj = self.builder.get_object(identifier)
            if not obj:
                log.warning("Object `%s` not found", identifier)
                continue

            objects.append(obj)
            value = self.get_value(section=item[0], type=item[1])

            if item[-1] == "btn":
                if not refresh:
                    obj.connect("clicked", self.show_detail, item)
                if not value:
                    obj.set_sensitive(False)
                else:
                    obj.set_sensitive(True)

            if item[-1] == "label":
                obj.set_text(str(value))

            if value > 0:
                obj.get_style_context().add_class("bold")
            else:
                obj.get_style_context().remove_class("bold")

    def get_value(self, section, type):
        if section not in self.data:
            log.warning("Section `%s` not in `self.data`.", section)
            return 0
        if type not in self.data[section]:
            log.warning("Type `%s` not in `self.data['%s']`.", type, section)
            return 0
        return len(self.data[section][type])

    def show_detail(self, source, param):
        builder = utils.get_builder("dashboard_detail.ui")
        window = builder.get_object("window")
        window.set_transient_for(self.window)

        title = "{0} {1}".format(TYPES[param[1]], SECTIONS[param[0]])
        window.set_title(title)

        treeview = builder.get_object("detail-treeview")
        treeview.set_property("enable-grid-lines", True)

        # Create headers
        text_renderer = Gtk.CellRendererText()
        text_renderer.set_property("wrap_mode", Pango.WrapMode.WORD_CHAR)
        text_renderer.set_property("wrap_width", 200)

        # Renderer for quantities, right-aligned, monospace font
        right_renderer = Gtk.CellRendererText()
        right_renderer.set_property("family-set", True)
        right_renderer.set_property("family", "mono")
        right_renderer.set_property("xalign", 1.0)
        right_renderer.set_property("xpad", 10)

        column = Gtk.TreeViewColumn(_("Name"), text_renderer, text=0)
        column.set_expand(True)
        treeview.append_column(column)

        # Format: xx/yy (current qty/required qty)
        column = Gtk.TreeViewColumn(_("Quantity"), right_renderer, text=1)
        treeview.append_column(column)

        if param[1] == "missing":
            # Missing = required - current quantity
            column = Gtk.TreeViewColumn(_("Missing"), right_renderer, text=2)
            treeview.append_column(column)
        elif param[1] in ["perished", "warning"]:
            column = Gtk.TreeViewColumn(_("Expiry"), text_renderer, text=2)
            treeview.append_column(column)
        elif param[1] == "nc":
            column = Gtk.TreeViewColumn(_("Non conformity"), text_renderer, text=2)
            column.set_expand(True)
            treeview.append_column(column)

        treeview.set_model(
            self.create_list_store(section=param[0], type=param[1])
            )

        builder.connect_signals({
            "copy-txt": (self.copy, "txt", param),
            "copy-csv": (self.copy, "csv", param)
        })

        window.show()

    def copy(self, source, output, param):
        section = param[0]
        type = param[1]

        if section not in self.data:
            log.warning("Section `%s` not in `self.data`.", section)
            return None
        if type not in self.data[section]:
            log.warning("Type `%s` not in `self.data['%s']`.", type, section)
            return None

        elements = self.data[section][type]

        header = get_header(output, section, type)

        parser = DataParser(elements, section, type, self.params)
        items = parser.get_items()

        if output == "txt":
            self.copy_as_txt(
                items=items,
                type=type,
                header=header
                )
        else:
            output = tempfile.NamedTemporaryFile(
                prefix="pharmaship_",
                suffix=".csv",
                delete=False
                )
            with open(output.name, "w", newline='') as csvfile:
                self.copy_as_csv(
                    items=items,
                    fields=header,
                    tmp_file=csvfile
                    )

            utils.open_file(output.name)

    def copy_as_txt(self, items, type, header):
        result = []
        result.append("\t".join(header))

        for item in items:
            if type == "missing":
                res = (
                    item["full_name"],
                    "{0}/{1}".format(item["current_quantity"], item["required_quantity"]),
                    str(item["missing_quantity"]),
                    )
                result.append("\t".join(res))
            elif type in ["perished", "warning"]:
                res = (
                    item["full_name"],
                    str(item["quantity"]),
                    item["full_date"],
                    )
                result.append("\t".join(res))
            elif type == "nc":
                res = (
                    item["full_name"],
                    str(item["quantity"]),
                    item["full_nc"],
                    )
                result.append("\t".join(res))

        result_text = "\n".join(result)

        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(result_text, -1)
        return True

    def copy_as_csv(self, items, fields, tmp_file):
        writer = csv.DictWriter(tmp_file, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()

        for item in items:
            writer.writerow(item)

        return True

    def create_list_store(self, section, type):
        if section not in self.data:
            log.warning("Section `%s` not in `self.data`.", section)
            return None
        if type not in self.data[section]:
            log.warning("Type `%s` not in `self.data['%s']`.", type, section)
            return None

        # Name, quantity, exp-date, required_qty
        list_store = Gtk.ListStore(str, str, str)

        elements = self.data[section][type]

        parser = DataParser(elements, section, type, self.params)
        items = parser.get_items()

        for item in items:
            if type == "missing":
                list_store.append((
                    item["full_name"],
                    "{0}/{1}".format(item["current_quantity"], item["required_quantity"]),
                    str(item["missing_quantity"]),
                    ))
            elif type in ["perished", "warning"]:
                list_store.append((
                    item["full_name"],
                    str(item["quantity"]),
                    item["full_date"],
                ))
            elif type == "nc":
                list_store.append((
                    item["full_name"],
                    str(item["quantity"]),
                    item["full_nc"],
                ))

        return list_store

    def get_molecules(self):
        data = parsers.medicines.parser(self.params)
        self.data["molecules"] = get_data_items(data)
        query_count_all()

    def get_equipment(self):
        data = parsers.equipment.parser(self.params)
        self.data["equipment"] = get_data_items(data)
        query_count_all()

    def get_rescue_bag(self):
        raw_data = parsers.rescue_bag.parser(self.params)
        data = {"data": raw_data["all"]["elements"]}
        self.data["rescue_bag"] = get_data_items(data)
        query_count_all()

    def get_first_aid_kit(self):
        raw_data = parsers.first_aid.parser(self.params)
        data = {}
        for kit in raw_data:
            data[kit["name"]] = kit["elements"]
        self.data["first_aid_kit"] = get_data_items(data)
        query_count_all()

    def get_laboratory(self):
        data = {"data": parsers.laboratory.parser(self.params)}
        self.data["laboratory"] = get_data_items(data)
        query_count_all()

    def get_telemedical(self):
        data = {"data": parsers.telemedical.parser(self.params)}
        self.data["telemedical"] = get_data_items(data)
        query_count_all()

    # Visual dashboards
    def graphic_condition(self):
        """Create a graph showing situation of elements per category."""
        canvas = dispatch.figure(self.data, self.params.setting)
        graphicbox = self.builder.get_object("graphics")
        graphicbox.pack_start(canvas, True, True, 0)
        graphicbox.show_all()
