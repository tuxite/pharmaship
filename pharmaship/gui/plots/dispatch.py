# -*- coding: utf-8 -*-
from django.utils.translation import gettext as _

import numpy as np

from pharmaship.core.utils import log

from pharmaship.gui.plots import utils

try:
    from matplotlib.backends.backend_gtk3agg import (
        FigureCanvasGTK3Agg as FigureCanvas)
except Exception:
    # To avoid errors when testing in Docker container
    from matplotlib.backend_bases import FigureCanvasBase as FigureCanvas

from matplotlib.figure import Figure

KEYS = [
    "missing",
    "perished",
    "warning",
    "nc"
]

def get_values(key, data):
    """Return a Dict of values from `data[key]`."""
    if key not in data:
        return {
            "values": [0, 0, 0, 0, 0],
            "total": 0
            }

    result = {
        "values": [],
        "total": data[key]["total"]
    }

    for item in KEYS:
        result["values"].append(len(data[key][item]))
    result["values"].append(data[key]["in_range"])

    return result



def figure(data, params):
    """Create a graph showing situation of elements per category."""
    category_names = [
        {
            "name": _('Missing'),
            "color": "#2e3436",
        },
        {
            "name": _('Perished'),
            "color": "#a40000",
        },
        {
            "name": _('Near expiry'),
            "color": "#f57900",
        },
        {
            "name": _('Non-conform'),
            "color": "#3465a4",
        },
        {
            "name": _('In range'),
            "color": "#069a17",
        },
    ]

    results = {
        "molecules": {
            "label": _("Medicines"),
        },
        "equipment": {
            "label": _("Equipment"),
        },
        "rescue_bag": {
            "label": _("Rescue bags"),
        },
        "first_aid_kit": {
            "label": _("First Aid Kits"),
        }
    }
    if params.has_telemedical:
        results["telemedical"] = {
            "label": _("Telemedical"),
        }
    if params.has_laboratory:
        results["laboratory"] = {
            "label": _("Laboratory"),
        }

    for item in results:
        results[item].update(get_values(item, data))

    fig = Figure(figsize=(5, 2), dpi=100, facecolor="#00000000")
    ax = fig.add_subplot()

    labels = []
    values = []
    totals = []
    for item in results:
        labels.append(results[item]["label"])
        values.append(results[item]["values"])
        totals.append(results[item]["total"])

    totals = np.array(totals)

    data = np.array(values)
    data_cum = data.cumsum(axis=1)

    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, 1)

    for i in range(len(category_names)):
        _values = data[:, i]
        _values_cum = data_cum[:, i]
        widths = np.divide(_values, totals, out=np.zeros(_values.shape, dtype=float), where=totals!=0)
        starts = np.divide(_values_cum, totals, out=np.zeros(_values_cum.shape, dtype=float), where=totals!=0) - widths
        ax.barh(
            labels,
            widths,
            left=starts,
            height=0.5,
            label=category_names[i]["name"],
            color=category_names[i]["color"]
            )
        xcenters = starts + widths / 2

        text_color = utils.fg_color(category_names[i]["color"])
        for y, (x, c) in enumerate(zip(xcenters, _values)):
            if c == 0:
                continue
            ax.text(x, y, str(int(c)), ha='center', va='center',
                    color=text_color)

    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')

    canvas = FigureCanvas(fig)  # a Gtk.DrawingArea
    canvas.set_size_request(800, 300)
    return canvas
