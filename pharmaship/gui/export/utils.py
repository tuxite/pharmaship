# -*- coding: utf-8 -*-
"""Utility functions for exporting data in PDF."""
import tempfile
import os.path

from django.template import Template
from django.utils import translation
from django.conf import settings

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from pharmaship.core.utils import log, query_count_all


def export_pdf(html_string, filename):
    """Export the equipment inventory in PDF."""
    css_path = os.path.join(settings.PHARMASHIP_REPORTS, filename)
    try:
        with open(css_path, "r") as fdesc:
            css_string = fdesc.read()
    except IOError as error:
        log.error("CSS file not readable: %s", error)
        return None

    # Create a temporary file
    tmp_file = tempfile.NamedTemporaryFile(
        prefix="pharmaship_",
        suffix=".pdf",
        delete=False
        )

    font_config = FontConfiguration()
    html = HTML(
        string=html_string,
        base_url=str(settings.PHARMASHIP_REPORTS)
        )
    css = CSS(
        string=css_string,
        font_config=font_config,
        base_url=str(settings.PHARMASHIP_REPORTS)
        )
    html.write_pdf(
        target=tmp_file.name,
        stylesheets=[css],
        font_config=font_config
        )

    query_count_all()

    return tmp_file.name


def get_template(filename, lang):
    """Return a Django template."""
    template_path = os.path.join(settings.PHARMASHIP_REPORTS, filename)

    try:
        with open(template_path, "r") as fdesc:
            template_string = fdesc.read()
    except IOError as error:
        log.error("File not readable. %s", error)
        return False

    # Force language. If not, LANGUAGE_CODE in django settings is used.
    translation.activate(lang)

    # Create Django template
    template = Template(template_string)

    return template
