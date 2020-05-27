# -*- coding: utf-8 -*-
"""Export utility class for Rescue Bag Inventory."""
import datetime

from django.utils.translation import gettext as _
from django.template import Context

from pharmaship.gui.export.utils import export_pdf, get_template

from pharmaship.inventory.parsers.rescue_bag import parser

TEMPLATE = "rescue_bag.html"
CSS = "report.css"


class Export:
    """Class for pdf export of rescue bags."""

    def __init__(self, params):
        """Initialize the class.

        `params`: GlobalParameters instance.
        """
        self.params = params

    def pdf_print(self):
        """Export the rescue bags inventory in PDF."""
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

        data = parser(self.params)

        # Create context
        context = Context({
            "title": _("Rescue Bag Inventory"),
            "vessel": self.params.vessel,
            "allowance_list": self.params.allowances,
            "data": data,
            "now": datetime.datetime.utcnow(),
            "expiry_date": self.params.today,
            "generator": "Pharmaship [proof-of-concept]"
            })

        html_string = template.render(context)

        return html_string
