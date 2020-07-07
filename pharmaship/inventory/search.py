# -*- coding: utf-8; -*-
"""Pharmaship inventory module."""
from django.db.models import Q
from django.utils.translation import gettext as _

from pharmaship.core.utils import log, query_count_all

from pharmaship.inventory import models
from pharmaship.inventory.utils import req_qty_element


def location_display(location_id_list, locations):
    """Return list of human-readable locations.

    The format of ``locations`` is the same as ``params.locations``.

    :param list(int) location_id_list: List of Location ID to display.
    :param list locations: List of all parsed \
    :class:`pharmaship.inventory.models.Location` instances.

    :return: List of strings representing each selected Location.
    :rtype: list(str)
    """
    result = []
    for item in locations:
        if item["id"] in location_id_list:
            result.append(" > ".join(item["sequence"]))

    return result


def get_quantity(transactions):
    """Get current quantity from a set of transactions.

    Caution: This method does not check that the transactions correspond all
    to the same ``content_object``.

    :param django.db.models.query.QuerySet transactions: Set of \
    :class:`pharmaship.inventory.models.QtyTransaction`.

    :return: Quantity
    :rtype: int
    """
    result = 0
    for transaction in transactions:
        if transaction.transaction_type in [1, 8]:
            result = transaction.value
        else:
            result -= transaction.value
    return result


def search(text, params):
    """Return the search results from a long enough text.

    To avoid unnecessary search, text length must be at least 2 chars.

    The method searches into medicines, equipment, laboratory and telemedical
    sets.

    The results are sorted by "parent" (Molecule/Equipment) and contains
    required quantities for each set if any, current quantity, group
    (MoleculeGroup or EquipmentGroup) and other names previously encountered
    (in Medicine and Article records).

    :param str text: String to search in the different database models.
    :param object params: Global Parameters of the application \
    (:class:`pharmaship.gui.view.GlobalParameters`)

    :return: List of parsed results. See ``pharmaship/schemas/search.json`` \
    for details.
    :rtype: list
    """
    if len(text) < 2:
        return []

    result = []

    result += get_molecules(text,  params)

    result += get_equipments(text, params)

    query_count_all()

    return result


def parse_items(items):
    """Return the list of instances ID and dictionary of encountered locations.

    :param django.db.models.query.QuerySet items: Set of items:

        * :class:`pharmaship.inventory.models.Article` or
        * :class:`pharmaship.inventory.models.Medicine`.

    :return: Tuple of ID list and locations dictionary
    :rtype: tuple(list, dict)
    """
    id_list = []
    locations = {}
    for item in items:
        id_list.append(item.parent_id)
        if item.parent_id not in locations:
            locations[item.parent_id] = {}
        locations[item.parent_id][item.location_id] = None

    return id_list, locations


def get_molecules(text, params):
    """Return a list of parsed molecules related to searched text.

    :param str text: String to search in the different database models.
    :param object params: Global Parameters of the application \
    (:class:`pharmaship.gui.view.GlobalParameters`)

    :return: List of parsed results. See ``pharmaship/schemas/search.json`` \
    for details.
    :rtype: list
    """
    result = []

    # Medicines
    medicines = models.Medicine.objects.filter(
        name__icontains=text).prefetch_related("location")
    id_list, locations = parse_items(medicines)

    # Molecules
    molecules = models.Molecule.objects.filter(
        Q(name__icontains=text) | Q(id__in=id_list)
        ).prefetch_related("medicines", "medicines__transactions", "group")
    req_qty_list = models.MoleculeReqQty.objects.filter(
        allowance__in=params.allowances
        ).prefetch_related('base', 'allowance')

    for item in molecules:
        if item.id not in locations:
            locations[item.id] = {}

        item_locations = location_display(
            locations[item.id].keys(),
            locations=params.locations
            )

        item_dict = {
            "id": item.id,
            "parent_name": item.name,
            "details": "{0} - {1}".format(item.get_dosage_form_display(), item.composition),
            "group": str(item.group),
            "other_names": [],
            "locations": item_locations,
            "type": [],
            "quantity": 0,
            "required": 0
        }

        required_quantity, _allowance = req_qty_element(item, req_qty_list)
        if required_quantity > 0:
            item_dict["type"].append({
                "label": _("Medicines"),
                "name": "medicines"
                })
            item_dict["required"] += required_quantity

        for medicine in item.medicines.all():
            if not medicine.used:
                item_dict["quantity"] += get_quantity(medicine.transactions.all())
            if medicine.name == item.name:
                continue
            item_dict["other_names"].append(medicine.name)

        result.append(item_dict)
    return result


def get_equipments(text, params):
    """Return a list of parsed equipments related to searched text.

    :param str text: String to search in the different database models.
    :param object params: Global Parameters of the application \
    (:class:`pharmaship.gui.view.GlobalParameters`)

    :return: List of parsed results. See ``pharmaship/schemas/search.json`` \
    for details.
    :rtype: list
    """
    result = []

    # Articles
    articles = models.Article.objects.filter(name__icontains=text)
    id_list, locations = parse_items(articles)

    # Equipment
    equipments = models.Equipment.objects.filter(
        Q(name__icontains=text) | Q(id__in=id_list)
        ).prefetch_related("articles", "articles__transactions", "group")

    req_qty_list = models.EquipmentReqQty.objects.filter(
        allowance__in=params.allowances
        ).prefetch_related('base', 'allowance')
    if params.setting.has_telemedical:
        telemedical_list = models.TelemedicalReqQty.objects.filter(
            allowance__in=params.allowances
            ).prefetch_related('base', 'allowance')
    else:
        telemedical_list = []
    if params.setting.has_laboratory:
        laboratory_list = models.LaboratoryReqQty.objects.filter(
            allowance__in=params.allowances
            ).prefetch_related('base', 'allowance')
    else:
        laboratory_list = []

    for item in equipments:
        if item.id not in locations:
            locations[item.id] = {}

        item_locations = location_display(
            locations[item.id].keys(),
            locations=params.locations
            )

        item_dict = {
            "id": item.id,
            "parent_name": item.name,
            "details": item.packaging,
            "group": str(item.group),
            "other_names": [],
            "locations": item_locations,
            "type": [],
            "quantity": 0,
            "required": 0
        }

        required_quantity, _allow = req_qty_element(item, req_qty_list)
        if required_quantity > 0:
            item_dict["type"].append({
                "label": _("Equipment"),
                "name": "equipment"
                })
            item_dict["required"] += required_quantity

        if laboratory_list:
            required_quantity, _allow = req_qty_element(item, laboratory_list)
            if required_quantity > 0:
                item_dict["type"].append({
                    "label": _("Laboratory"),
                    "name": "laboratory"
                    })
                item_dict["required"] += required_quantity

        if telemedical_list:
            required_quantity, _allow = req_qty_element(item, telemedical_list)
            if required_quantity > 0:
                item_dict["type"].append({
                    "label": _("Telemedical"),
                    "name": "telemedical"
                    })
                item_dict["required"] += required_quantity

        for article in item.articles.all():
            if not article.used:
                item_dict["quantity"] += get_quantity(article.transactions.all())
            if article.name == item.name:
                continue
            item_dict["other_names"].append(article.name)

        result.append(item_dict)
    return result
