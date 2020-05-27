# -*- coding: utf-8 -*-
"""Export utility class for exporting all inventories."""
import datetime
import tempfile
import importlib
from pathlib import Path

from PyPDF2 import PdfFileMerger, PdfFileReader

from django.utils.translation import gettext as _
from django.template import Context

from pharmaship.core.utils import log
from pharmaship.gui.export.utils import export_pdf, get_template
import pharmaship.inventory.parsers as parsers

TEMPLATE_MISSING = "export_missing.html"
TEMPLATE_PERISHED = "export_perished.html"
CSS = "report.css"


class Export:
    """Class for pdf export of all inventories."""

    def __init__(self, params):
        """Initialize the class.

        `params`: GlobalParameters instance.
        """
        self.params = params

        self.inventories = [
            "medicines",
            "equipment",
            "rescue_bag",
            "first_aid_kits"
            ]
        if self.params.setting.has_laboratory:
            self.inventories.append("laboratory")
        if self.params.setting.has_telemedical:
            self.inventories.append("telemedical")

    def __generate_pdfs(self):
        file_list = []
        for module in self.inventories:
            try:
                module_pkg = importlib.import_module("pharmaship.gui.export." + module)
            except ImportError as error:
                log.error("Module %s has no gui.export function.", module)
                log.error(error)
                continue

            if not hasattr(module_pkg, "Export"):
                log.error("Module %s has no Export class.", module)
                continue

            cls = module_pkg.Export(self.params)
            filename = cls.pdf_print()
            file_list.append(filename)

        return file_list

    def pdf_print(self):
        file_list = self.__generate_pdfs()
        merger = PdfFileMerger()

        for pdf in file_list:
            doc = PdfFileReader(pdf)
            info = doc.getDocumentInfo()
            merger.append(pdf, bookmark=info["/Title"].split(" - Pharmaship")[0])

        # Create a temporary file
        tmp_file = tempfile.NamedTemporaryFile(
            prefix="pharmaship_all_",
            suffix=".pdf",
            delete=False
            )

        merger.write(tmp_file.name)
        merger.close()

        # Cleanup
        for pdf in file_list:
            Path(pdf).unlink()

        return tmp_file.name


class ExportMissing:
    """Class for pdf export of all missing elements."""

    def __init__(self, params, data):
        """Initialize the class.

        `params`: GlobalParameters instance.
        """
        self.params = params
        self.data = data

    def pdf_print(self):
        """Export the equipment inventory in PDF."""
        html_string = self.__export_html(TEMPLATE_MISSING)

        tempfilename = export_pdf(html_string, CSS)
        return tempfilename

    def __export_html(self, template_filename):
        template = get_template(
            template_filename,
            self.params.application.lang
            )
        if not template:
            return False

        # Get data
        result = {
            "molecules": [],
            "equipment": [],
            "telemedical": {},
            "laboratory": {},
            "first_aid_kit": {},
        }
        # self.data

        data = {}
        items = parsers.medicines.parser(self.params)
        for group in items:
            subgroup = []
            for item in items[group]:
                if item["required_quantity"] > item["quantity"]:
                    item["missing_quantity"] = item["required_quantity"] - item["quantity"]
                    subgroup.append(item)

            if len(subgroup) > 0:
                data[group] = subgroup

        result["molecules"] = data

        data = {}
        items = parsers.equipment.parser(self.params)
        for group in items:
            subgroup = []
            for item in items[group]:
                if item["required_quantity"] > item["quantity"]:
                    item["missing_quantity"] = item["required_quantity"] - item["quantity"]
                    subgroup.append(item)

            if len(subgroup) > 0:
                data[group] = subgroup

        result["equipment"] = data

        data = {}
        kits = parsers.first_aid.parser(self.params)
        for kit in kits:
            for item in kit["elements"]:
                if item["required_quantity"] > item["quantity"]:
                    id = "{type:03d}-{id:03d}".format(**item["parent"])
                    if id not in data:
                        data[id] = item
                        data[id]["missing_quantity"] = 0

                    data[id]["missing_quantity"] += item["required_quantity"] - item["quantity"]

        result["first_aid_kit"] = data

        if self.params.setting.has_laboratory:
            data = []
            items = parsers.laboratory.parser(self.params)
            for item in items:
                if item["required_quantity"] > item["quantity"]:
                    item["missing_quantity"] = item["required_quantity"] - item["quantity"]
                    data.append(item)

            result["laboratory"] = data

        if self.params.setting.has_telemedical:
            data = []
            items = parsers.telemedical.parser(self.params)
            for item in items:
                if item["required_quantity"] > item["quantity"]:
                    item["missing_quantity"] = item["required_quantity"] - item["quantity"]
                    data.append(item)

            result["telemedical"] = data

        # Create context
        context = Context({
            "title": _("Missing Items"),
            "vessel": self.params.vessel,
            "allowance_list": self.params.allowances,
            "data": result,
            "laboratory": self.params.setting.has_laboratory,
            "telemedical": self.params.setting.has_telemedical,
            "now": datetime.datetime.utcnow(),
            "expiry_date": self.params.today,
            "generator": "Pharmaship [proof-of-concept]"
            })

        html_string = template.render(context)

        return html_string


class ExportPerished:
    """Class for pdf export of all perished elements."""

    def __init__(self, params, data):
        """Initialize the class.

        `params`: GlobalParameters instance.
        """
        self.params = params
        self.data = data

    def pdf_print(self):
        """Export the equipment inventory in PDF."""
        html_string = self.__export_html(TEMPLATE_PERISHED)

        tempfilename = export_pdf(html_string, CSS)
        return tempfilename

    def __export_html(self, template_filename):
        template = get_template(
            template_filename,
            self.params.application.lang
            )
        if not template:
            return False

        # Get data
        result = {
            "molecules": [],
            "equipment": [],
            "telemedical": {},
            "laboratory": {},
            "first_aid_kit": {},
        }
        # self.data

        data = {}
        items = parsers.medicines.parser(self.params)
        for group in items:
            subgroup = []
            for item in items[group]:
                if item["has_date_expired"]:
                    subgroup.append(item)

            if len(subgroup) > 0:
                data[group] = subgroup

        result["molecules"] = data

        data = {}
        items = parsers.equipment.parser(self.params)
        for group in items:
            subgroup = []
            for item in items[group]:
                if item["has_date_expired"]:
                    subgroup.append(item)

            if len(subgroup) > 0:
                data[group] = subgroup

        result["equipment"] = data

        data = {}
        kits = parsers.first_aid.parser(self.params)
        for kit in kits:
            for item in kit["elements"]:
                if not item["has_date_expired"]:
                    continue

                id = "{type:03d}-{id:03d}".format(**item["parent"])
                if id not in data:
                    data[id] = []

                for subitem in item["contents"]:
                    if not subitem["expired"]:
                        continue

                    data[id].append(subitem)

        result["first_aid_kit"] = data

        if self.params.setting.has_laboratory:
            data = []
            items = parsers.laboratory.parser(self.params)
            for item in items:
                if item["has_date_expired"]:
                    data.append(item)

            result["laboratory"] = data

        if self.params.setting.has_telemedical:
            data = []
            items = parsers.telemedical.parser(self.params)
            for item in items:
                if item["has_date_expired"]:
                    data.append(item)

            result["telemedical"] = data

        # Create context
        context = Context({
            "title": _("Perished Items"),
            "vessel": self.params.vessel,
            "allowance_list": self.params.allowances,
            "data": result,
            "laboratory": self.params.setting.has_laboratory,
            "telemedical": self.params.setting.has_telemedical,
            "now": datetime.datetime.utcnow(),
            "expiry_date": self.params.today,
            "generator": "Pharmaship [proof-of-concept]"
            })

        html_string = template.render(context)

        return html_string
