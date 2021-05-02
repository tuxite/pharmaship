# -*- coding: utf-8 -*-
import datetime
import locale

from pharmaship.core.utils import log

from pharmaship.inventory import models
from pharmaship.inventory.utils import req_qty_element
# from purchase.models import Item

from pharmaship.inventory.parsers.equipment import parser_element


# Pre-treatment function
def parser(params):
    """Parse the database to render a list of Equipment/Article.

    Process database data and set flags on articles missing, expired or \
    reaching near expiry.

    Only equipement with \
    :class:`pharmaship.inventory.models.TelemedicalReqQty` is listed.

    See ``pharmaship/schemas/parsers/telemedical.json`` for details.

    :param object params: Global Parameters of the application \
    (:class:`pharmaship.gui.view.GlobalParameters`)

    :return: List of Equipment.
    :rtype: list
    """
    data = {}
    allowance_list = params.allowances
    location_list = params.locations
    warning_delay = params.setting.expire_date_warning_delay
    today = params.today
    # Required quantities for listed allowances
    req_qty_list = models.TelemedicalReqQty.objects.filter(allowance__in=allowance_list).prefetch_related('base', 'allowance')
    # Equipment list
    equipment_ids = req_qty_list.values_list("base_id", flat=True)
    equipments = models.Equipment.objects.filter(id__in=equipment_ids).distinct().prefetch_related('tag', 'articles').order_by('name')
    # Article quantity transaction list
    data["qty_transactions"] = models.QtyTransaction.objects.filter(content_type=params.content_types['article']).order_by("date")

    # Ordered items
    # data["ordered_items"] = Item.objects.filter(
    #     content_type=ContentType.objects.get_for_model(models.Equipment),
    #     requisition__status__in=[4,5])
    # Locations
    data["locations"] = location_list

    if today is None:
        today = datetime.date.today()

    result = []

    for equipment in equipments:
        element = parser_element(equipment, data, warning_delay, today)
        element["required_quantity"], element["allowance"] = req_qty_element(equipment, req_qty_list)
        result.append(element)

    result = sorted(
        result,
        key=lambda item: locale.strxfrm(item["name"])
        )
    return result
