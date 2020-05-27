# -*- coding: utf-8 -*-
"""Export utility class for Equipment Inventory."""
import datetime

from django.utils.translation import gettext as _
from django.template import Context

from pharmaship.gui.export.utils import export_pdf, get_template

from pharmaship.inventory.parsers.equipment import parser

TEMPLATE = "equipment.html"
CSS = "report.css"


class Export:
    """Class for pdf export of medical equipment."""

    def __init__(self, params):
        """Initialize the class.

        `params`: GlobalParameters instance.
        """
        self.params = params

    def pdf_print(self):
        """Export the equipment inventory in PDF."""
        html_string = self.__export_html(TEMPLATE)

        tempfilename = export_pdf(html_string, CSS)
        return tempfilename

    def __export_html(self, template_filename):
        template = get_template(
            template_filename,
            self.params.application.lang
            )
        if not template:
            return False

        # Get data (dict type)
        data = parser(self.params)

        # Create context
        context = Context({
            "title": _("Equipment Inventory"),
            "vessel": self.params.vessel,
            "allowance_list": self.params.allowances,
            "data": data,
            "now": datetime.datetime.utcnow(),
            "expiry_date": self.params.today,
            "generator": "Pharmaship [proof-of-concept]"
            })

        html_string = template.render(context)

        return html_string
