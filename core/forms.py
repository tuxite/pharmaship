# -*- coding: utf-8; -*-
from django.forms import widgets
from django.utils import formats

class DateInput(widgets.DateTimeBaseInput):
    """Customized class for Date inputs with the HTML5 date type and
    placeholder for browsers not supporting this HTML5 type."""
    input_type = 'date'

    def __init__(self, attrs=None, format=None):
        super(DateInput, self).__init__(attrs)
        self.format = '%Y-%m-%d'
        self.attrs = {'placeholder': 'YYYY-MM-DD'}

    def _format_value(self, value):
        return formats.localize_input(value, self.format)
