# -*- coding: utf-8 -*-
import datetime
import copy

from django.utils.translation import gettext as _

from pharmaship.core.utils import log

from pharmaship.inventory import models
# from purchase.models import Item


def get_required(params):
    # Get required quantities
    req_qty_list = models.FirstAidKitReqQty.objects.filter(allowance__in=params.allowances).select_related('allowance')
    required_quantities = {
        "molecules": {},
        "equipments": {},
    }
    for item in req_qty_list:
        if item.content_type_id == params.content_types["molecule"]:
            key = "molecules"
        else:
            key = "equipments"

        if item.object_id not in required_quantities[key]:
            required_quantities[key][item.object_id] = {
                "additional": 0,
                "maximum": 0,
                "detail": []
            }

        element = required_quantities[key][item.object_id]

        detail = {
            "name": item.allowance.name
            }
        if item.allowance.additional:
            element["additional"] += item.required_quantity
            detail["quantity"] = "+{0}".format(item.required_quantity)
        else:
            element["maximum"] = max(element["maximum"], item.required_quantity)
            detail["quantity"] = item.required_quantity

        element["detail"].append(detail)

    return required_quantities


def get_transactions(content_type, items):
    """Get transactions for selected `items`."""
    transactions = models.QtyTransaction.objects.filter(
        content_type_id=content_type,
        object_id__in=items
        ).order_by("date")

    result = {}
    for transaction in transactions:
        if transaction.object_id not in result:
            result[transaction.object_id] = 0

        if transaction.transaction_type in [1, 8]:
            result[transaction.object_id] = transaction.value
        else:
            result[transaction.object_id] -= transaction.value

    return result


def create_molecule(item, content_type, required=None):
    result = {
        "name": str(item),
        "required_quantity": 0,
        "quantity": 0,
        "allowance": [],
        "remark": item.remark,
        "picture": None,
        "available": [],
        "contents": [],
        "type": "molecule",
        "perishable": True,
        "consumable": True,
        "has_nc": False,
        "has_date_warning": False,
        "has_date_expired": False,
        "locations": [],
        "exp_dates": [],
        "parent": {
            "type": content_type,
            "id": item.id
        }
    }

    if required:
        result["required_quantity"] = required[item.id]["maximum"] + required[item.id]["additional"]
        result["allowance"] = required[item.id]["detail"]

    return result


def create_equipment(item, content_type, required):
    result = {
        "name": str(item),
        "required_quantity": 0,
        "quantity": 0,
        "allowance": [],
        "remark": item.remark,
        "picture": item.picture,
        "available": [],
        "contents": [],
        "type": "equipment",
        "perishable": item.perishable,
        "consumable": item.consumable,
        "has_nc": False,
        "has_date_warning": False,
        "has_date_expired": False,
        "locations": [],
        "exp_dates": [],
        "parent": {
            "type": content_type,
            "id": item.id
        }
    }

    if item.id in required:
        result["required_quantity"] = required[item.id]["maximum"] + required[item.id]["additional"]
        result["allowance"] = required[item.id]["detail"]

    return result


def get_available_medicines(element, content_type_id, qty_transactions):
    result = []

    for item in element.medicines.all():
        item_dict = {
            "id": item.id,
            "name": item.name,
            "exp_date": item.exp_date,
            "quantity": 0,
            "nc": {
                "composition": item.nc_composition,
                "molecule": item.nc_molecule
            },
            "type": content_type_id,
        }

        if item.id in qty_transactions:
            item_dict["quantity"] = qty_transactions[item.id]

        result.append(item_dict)

    return result


def get_available_articles(element, content_type_id, qty_transactions):
    result = []

    for item in element.articles.all():
        item_dict = {
            "id": item.id,
            "name": item.name,
            "exp_date": item.exp_date,
            "quantity": 0,
            "nc": {
                "packaging": item.nc_packaging
            },
            "type": content_type_id,
        }

        if item.id in qty_transactions:
            item_dict["quantity"] = qty_transactions[item.id]

        result.append(item_dict)

    return result


def get_subitems(params, kit, common):
    warning_delay = params.setting.expire_date_warning_delay
    today = params.today
    # Compute once the warning date from warning_delay days
    warning_date = today + datetime.timedelta(days=warning_delay)

    result = copy.deepcopy(common)

    subitem_list = kit.items.all()
    subitem_id_list = subitem_list.values_list("id", flat=True)
    qty_transactions = get_transactions(params.content_types["firstaidkititem"], subitem_id_list)

    for item in subitem_list:
        if item.used is True:
            continue

        child = {
            "id": item.id,
            "name": item.name,
            "exp_date": item.exp_date,
            "nc": item.nc,
            "remark": item.remark,
            "kit_id": kit.id,
            "quantity": 0,
            "expired": False,
            "warning": False
        }

        if item.content_type_id == params.content_types["molecule"]:
            parent = result["molecules"][item.object_id]
        elif item.content_type_id == params.content_types["equipment"]:
            parent = result["equipments"][item.object_id]
        else:
            # No parent
            continue

        if item.exp_date:
            parent["exp_dates"].append(item.exp_date)
            if item.exp_date <= warning_date:
                child['warning'] = True
                parent['has_date_warning'] = True
            if item.exp_date <= params.today:
                child['expired'] = True
                parent['has_date_expired'] = True

        if item.nc:
            parent["has_nc"] = True

        if item.id in qty_transactions:
            child["quantity"] = qty_transactions[item.id]
            parent["quantity"] += child["quantity"]

        parent["contents"].append(child)

    return result


def merge_elements(elements_dict):
    result = []

    for k, element in elements_dict["molecules"].items():
        result.append(element)

    for k, element in elements_dict["equipments"].items():
        result.append(element)

    return result

# Pre-treatment function
def parser(params, kits=None):
    result = []

    if kits is None:
        kits = models.FirstAidKit.objects.order_by("id").prefetch_related("items").all()[:params.setting.first_aid_kit]

    # Prepare required quantity lists
    required = get_required(params)

    equipment_id_list = required["equipments"].keys()
    equipment_list = models.Equipment.objects.filter(id__in=equipment_id_list).prefetch_related("articles")
    articles_id_list = equipment_list.values_list("articles__id", flat=True)
    articles_qty_transactions = get_transactions(
        content_type=params.content_types["article"],
        items=articles_id_list
        )

    molecule_id_list = required["molecules"].keys()
    molecule_list = models.Molecule.objects.filter(id__in=molecule_id_list).prefetch_related("medicines")
    medicines_id_list = molecule_list.values_list("medicines__id", flat=True)
    medicines_qty_transactions = get_transactions(
        content_type=params.content_types["medicine"],
        items=medicines_id_list
        )

    common = {
        "molecules": {},
        "equipments": {}
    }

    for molecule in molecule_list:
        element = create_molecule(molecule, params.content_types["molecule"], required["molecules"])
        element["available"] = get_available_medicines(
            content_type_id=params.content_types["medicine"],
            element=molecule,
            qty_transactions=medicines_qty_transactions
            )

        common["molecules"][molecule.id] = element

    for equipment in equipment_list:
        element = create_equipment(equipment, params.content_types["equipment"], required["equipments"])
        element["available"] = get_available_articles(
            content_type_id=params.content_types["article"],
            element=equipment,
            qty_transactions=articles_qty_transactions
            )

        common["equipments"][equipment.id] = element

    for kit in kits:
        kit_dict = {
            "id": kit.id,
            "name": kit.name,
            "location_id": kit.location_id,
            "elements": []
        }

        kit_dict["elements"] = merge_elements(get_subitems(params, kit, common))
        result.append(kit_dict)

    return result
