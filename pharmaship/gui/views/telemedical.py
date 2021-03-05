# -*- coding: utf-8 -*-
import gi
gi.require_version("Gtk", "3.0")  # noqa: E402
from gi.repository import Gtk

from pharmaship.core.utils import log, query_count_all

from pharmaship.inventory.parsers.telemedical import parser

from pharmaship.gui.views.equipment import View as EquipmentView


class View(EquipmentView):
    def __init__(self, window, chosen=None):
        super().__init__(window, chosen=None)

    def parser(self, params):
        return parser(params)

    def create_grid(self, toggle_row_num=None):
        grid = Gtk.Grid()

        # Header
        self.grid_header(grid)

        data = parser(self.params)

        i = 0
        toggle_equipment = None

        for equipment in data:
            i += 1
            toggle_equipment = self.create_row(
                grid, equipment,
                toggle_equipment,
                toggle_row_num,
                i
                )

        # Toggle if active
        if toggle_row_num and toggle_equipment:
            self.toggle_article(
                source=None,
                grid=grid,
                equipment=toggle_equipment,
                row_num=toggle_row_num
                )

        query_count_all()

        return grid
