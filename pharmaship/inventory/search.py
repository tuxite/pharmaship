# -*- coding: utf-8; -*-
"""Pharmaship inventory module."""
from django.db.models import Q
from django.utils.translation import gettext as _

from pharmaship.core.utils import log, query_count_all

from pharmaship.inventory import models
from pharmaship.inventory.utils import req_qty_element


def location_display(location_id_list, locations):
    result = []
    for item in locations:
        if item["id"] in location_id_list:
            result.append(" > ".join(item["sequence"]))

    return result


def get_quantity(transactions):
    result = 0
    for transaction in transactions:
        if transaction.transaction_type in [1, 8]:
            result = transaction.value
        else:
            result -= transaction.value
    return result


def search(text, params):
    # Search only if more than 2 chars
    if len(text) < 2:
        return []

    result = []

    molecule_id_list = []
    equipment_id_list = []

    loc = {
        "molecule": {},
        "equipment": {}
    }
    locations = params.locations
    allowance_list = params.allowances

    # Medicines
    medicines = models.Medicine.objects.filter(name__icontains=text).prefetch_related("location")
    for item in medicines:
        molecule_id_list.append(item.parent_id)
        if item.parent_id not in loc["molecule"]:
            loc["molecule"][item.parent_id] = {}
        loc["molecule"][item.parent_id][item.location_id] = None

    # Molecules
    molecules = models.Molecule.objects.filter(
        Q(name__icontains=text) | Q(id__in=molecule_id_list)
        ).prefetch_related("medicines", "medicines__transactions", "group")
    req_qty_list = models.MoleculeReqQty.objects.filter(
        allowance__in=allowance_list
        ).prefetch_related('base', 'allowance')

    for item in molecules:
        if item.id not in loc["molecule"]:
            loc["molecule"][item.id] = {}

        item_locations = location_display(
            loc["molecule"][item.id].keys(),
            locations=locations
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

    # Articles
    articles = models.Article.objects.filter(name__icontains=text)
    for item in articles:
        equipment_id_list.append(item.parent_id)
        if item.parent_id not in loc["equipment"]:
            loc["equipment"][item.parent_id] = {}
        loc["equipment"][item.parent_id][item.location_id] = None

    # Equipment
    equipments = models.Equipment.objects.filter(
        Q(name__icontains=text) | Q(id__in=equipment_id_list)
        ).prefetch_related("articles", "articles__transactions", "group")

    req_qty_list = models.EquipmentReqQty.objects.filter(
        allowance__in=allowance_list
        ).prefetch_related('base', 'allowance')
    if params.setting.has_telemedical:
        telemedical_list = models.TelemedicalReqQty.objects.filter(
            allowance__in=allowance_list
            ).prefetch_related('base', 'allowance')
    else:
        telemedical_list = []
    if params.setting.has_laboratory:
        laboratory_list = models.LaboratoryReqQty.objects.filter(
            allowance__in=allowance_list
            ).prefetch_related('base', 'allowance')
    else:
        laboratory_list = []

    for item in equipments:
        if item.id not in loc["equipment"]:
            loc["equipment"][item.id] = {}

        item_locations = location_display(
            loc["equipment"][item.id].keys(),
            locations=locations
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

        required_quantity, _allowance = req_qty_element(item, req_qty_list)
        if required_quantity > 0:
            item_dict["type"].append({
                "label": _("Equipment"),
                "name": "equipment"
                })
            item_dict["required"] += required_quantity

        if params.setting.has_laboratory:
            required_quantity, _allowance = req_qty_element(item, laboratory_list)
            if required_quantity > 0:
                item_dict["type"].append({
                    "label": _("Laboratory"),
                    "name": "laboratory"
                    })
                item_dict["required"] += required_quantity

        if params.setting.has_telemedical:
            required_quantity, _allowance = req_qty_element(item, telemedical_list)
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

    query_count_all()

    # Type: molecule/equipment
    # Name
    # Location
    # Current quantity
    # Required quantity?
    return result
