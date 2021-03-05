# -*- coding: utf-8 -*-
"""Parser for Equipment data."""
import datetime

from django.utils.translation import gettext as _

from pharmaship.core.utils import log

from pharmaship.inventory import models
from pharmaship.inventory.utils import req_qty_element, get_quantity
# from purchase.models import Item


# Pre-treatment function
def parser(params):
    """Parse the database to render a dict of EquipmentGroup/Equipment/Article.

    Process database data and set flags on articles missing, expired or \
    reaching near expiry.

    Only equipements with :class:`pharmaship.inventory.models.EquipmentReqQty`\
    are listed.

    Data is sorted by :class:`pharmaship.inventory.models.EquipmentGroup`.

    See ``pharmaship/schemas/parsers/equipment.json`` for details.

    :param object params: Global Parameters of the application \
    (:class:`pharmaship.gui.view.GlobalParameters`)

    :return: Dictionnary with list of Equipment by EquimentGroup.
    :rtype: dict(list)
    """
    allowance_list = params.allowances
    location_list = params.locations
    warning_delay = params.setting.expire_date_warning_delay
    today = params.today
    data = {}
    # Required quantities for listed allowances
    req_qty_list = models.EquipmentReqQty.objects.filter(allowance__in=allowance_list).prefetch_related('base', 'allowance')
    # Equipment list
    equipments = models.Equipment.objects.filter(allowances__in=allowance_list).distinct().prefetch_related('group', 'tag', 'articles').order_by('group', 'name')
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

    result = {}

    for equipment in equipments:
        element = parser_element(equipment, data, warning_delay, today)
        element["required_quantity"], element["allowance"] = req_qty_element(equipment, req_qty_list)
        # Do not add not required elemments with zero quantity
        if element["required_quantity"] == 0 and element["quantity"] == 0:
            continue

        if equipment.group not in result:
            result[equipment.group] = []

        result[equipment.group].append(element)

    return result


def parser_element(equipment, data, warning_delay, today=datetime.date.today()):
    """Parse the database to render a list of Equipment > Article.

    :param models.Equipment equipment: Equipment to parse
    :param dict data: Common data for parsing. Following keys must be present:

        * ``qty_transactions``: QuerySet of \
        :class:`pharmaship.inventory.models.QtyTransaction`
        * ``locations``: formatted list of \
        :class:`pharmaship.inventory.models.Location`

    :param datetime.date warning_delay: Date from which warning flag must be \
    set
    :param datetime.date today: Date from which expired flag must be set.

    :return: Formatted information with articles.
    :rtype: dict
    """
    # ordered_items = data["ordered_items"]
    qty_transactions = data["qty_transactions"]
    locations = data["locations"]

    element_dict = {}
    element_dict['id'] = equipment.id
    element_dict['name'] = equipment.name
    element_dict['packaging'] = equipment.packaging
    element_dict['remark'] = equipment.remark
    element_dict['perishable'] = equipment.perishable
    element_dict['consumable'] = equipment.consumable
    element_dict['picture'] = equipment.picture

    element_dict['locations'] = []
    # Ordered
    # element_dict['ordered'] = 0
    # for item in ordered_items:
    #     if item.object_id == equipment.id:
    #         element_dict['ordered'] += item.quantity
    # Tags
    element_dict['tag'] = equipment.tag
    # Quantity
    element_dict['quantity'] = 0
    element_dict['expiring_quantity'] = 0

    element_dict['articles'] = []
    element_dict['exp_dates'] = []
    element_dict['has_nc'] = False
    element_dict['has_date_warning'] = False
    element_dict['has_date_expired'] = False

    # Compute once the warning date from warning_delay days
    warning_date = today + datetime.timedelta(days=warning_delay)

    # Finding attached articles (Article)
    for article in equipment.articles.all():
        # Do not parse the used articles (quantity = 0)
        if article.used:
            continue
        item_dict = {}

        item_dict['id'] = article.id
        item_dict['name'] = article.name
        # Non conformity fields
        item_dict['nc_packaging'] = article.nc_packaging
        # Expiration date
        item_dict['exp_date'] = article.exp_date
        if article.exp_date:
            element_dict['exp_dates'].append(article.exp_date)
        # Check if the article is expired or not and if the expiry is within
        # the user-defined period
        # Consider "today" as already passed (that is why we use <= operator)
        item_dict['expired'] = False
        item_dict['warning'] = False
        if article.exp_date and article.exp_date <= warning_date:
            item_dict['warning'] = True
            element_dict['has_date_warning'] = True
        if article.exp_date and article.exp_date <= today:
            item_dict['expired'] = True
            element_dict['has_date_expired'] = True
        # Location

        # In case of unassigned location
        if article.location_id == 0:
            item_dict['location'] = {
                "sequence": [_("Unassigned")],
                "id": None,
                "parent": None,
                "rescue_bag": None
            }
            location_display = _("Unassigned")
        else:
            for item in locations:
                if article.location_id == item["id"]:
                    item_dict['location'] = item
                    location_display = " > ".join(item["sequence"])
                    if location_display not in element_dict['locations']:
                        element_dict['locations'].append(location_display)
        # Quantity
        item_dict['quantity'] = get_quantity(qty_transactions, article.id)

        if item_dict['quantity'] < 0:
            log.warning("Article (ID: %s) with negative quantity (%s)", item_dict["id"], item_dict["quantity"])

        # Adding the article quantity to the equipment quantity
        if (equipment.perishable and article.exp_date > today) or (equipment.perishable is not True):
            element_dict['quantity'] += item_dict['quantity']
            if item_dict['warning']:
                element_dict['expiring_quantity'] += item_dict['quantity']

        # Add the equipment_id in case of reverse search
        item_dict['equipment'] = {
            "id": equipment.id,
            "name": equipment.name,
            "packaging": equipment.packaging
            }

        # Packing
        if article.packing_name > 0:
            item_dict['packing'] = {
                "id": article.packing_name,
                "name": article.get_packing_name_display(),
                "content": article.packing_content
            }
        else:
            item_dict['packing'] = None

        # Remark
        item_dict['remark'] = article.remark

        # Adding the article dict to the list
        element_dict['articles'].append(item_dict)

        # If article has a non-conformity, set element_dict.has_nc to True
        if article.nc_packaging:
            element_dict["has_nc"] = True

    # Returning the result dictionnary
    return element_dict
