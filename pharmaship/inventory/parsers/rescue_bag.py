# -*- coding: utf-8 -*-
"""Utility functions for parsing/serializing Rescue Bag related data."""
import datetime

from django.utils.translation import gettext as _

from pharmaship.core.utils import log

from pharmaship.inventory import models


# Pre-treatment function
def parser(params):
    """Parse the database to render a list of Equipments & Molecules.

    Process database data and set flags on articles missing, expired or \
    reaching near expiry.

    Only equipement with :class:`pharmaship.inventory.models.RescueBagReqQty`\
    is listed.

    See ``pharmaship/schemas/parsers/rescue_bag`` for details.

    Resumed architecture of the method:

        1. Get required quantities: :py:func:`get_required`
        2. Get molecules & medicines: :py:func:`get_medicines`

          * Get transactions for medicines: :py:func:`get_transactions`
          * From Molecules list, create molecules: :py:func:`create_molecules`

                * For each Molecule, create a molecule dict: \
                :py:func:`create_molecules`

        3. Get equipments & articles: :py:func:`get_articles`

          * Get transactions for articles: :py:func:`get_transactions`
          * From Equipments list, create equipments: \
          :py:func:`create_equipments`

                * For each Equipment, create an equipment dict: \
                :py:func:`create_equipment`

        4. Merge bags: :py:func:`merge_bags`

    :param object params: Global Parameters of the application \
    (:class:`pharmaship.gui.view.GlobalParameters`)

    :return: Dictionnary of Rescue Bags.
    :rtype: dict
    """
    result = {
        "all": {
            "name": _("All Rescue Bags"),
            "location_id": None,
            "elements": []
        }
    }

    # List of locations linked to a bag for Queryset filtering
    location_ids = []

    rescue_bags = models.RescueBag.objects.all()
    for bag in rescue_bags:
        location_ids.append(bag.location_id)

    # Get all required molecules/equipments
    required = get_required(params)
    # Get medicines and articles
    # In the same time, get the related molecules and equipments
    molecules = get_medicines(params, required["molecules"], location_ids)
    equipments = get_articles(params, required["equipments"], location_ids)
    # Add the molecules and equipments to the main bag
    result["all"]["elements"] = [v for k, v in molecules.items()]
    result["all"]["elements"] += [v for k, v in equipments.items()]
    result = {**result, **merge_bags(rescue_bags, molecules, equipments)}

    return result


def create_molecules(id_list, required):
    """Create a dictionary of Molecules according to an ID list.

    :param list id_list: ID list of \
    :class:`pharmaship.inventory.models.Molecule`
    :param dict required: Dictionary of required quantities for molecules \
    (keys are Molecule ID).

    :return: Dictionary of molecule data
    :rtype: dict
    """
    molecules = models.Molecule.objects.filter(id__in=id_list).order_by("name")
    result = {}
    for molecule in molecules:
        result[molecule.id] = create_molecule(molecule, required)

    return result


def create_equipments(id_list, required):
    """Create a dictionary of Equipments according to an ID list.

    :param list id_list: ID list of \
    :class:`pharmaship.inventory.models.Equipment`
    :param dict required: Dictionary of required quantities for equipments \
    (keys are Equipment ID).

    :return: Dictionary of equipment data
    :rtype: dict
    """
    equipments = models.Equipment.objects.filter(id__in=id_list).order_by("name")
    result = {}
    for equipment in equipments:
        result[equipment.id] = create_equipment(equipment, required)

    return result


def get_transactions(content_type, items):
    """Get transactions for selected `items`.

    :param int content_type: ID of ContentType of items
    :param list items: List of items ID

    :return: Dictionary of compiled quantities for each item. Dict keys are \
    items ID.
    :rtype: dict
    """
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


def get_required(params):
    """Get required quantities.

    :param object params: Global Parameters of the application \
    (:class:`pharmaship.gui.view.GlobalParameters`)

    :return: A dictionary of required quantities sorted by type (molecule or \
    equipment) and subsequent item ID.
    :rtype: dict
    """
    req_qty_list = models.RescueBagReqQty.objects.filter(allowance__in=params.allowances).select_related('allowance')
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


def create_molecule(item, required=None):
    """Return a dictionary of a molecule.

    :param models.Molecule item: A Molecule instance.
    :param required: Dictionary of required quantities for molecules \
    (keys are Molecule ID).

    :return: Dictionary of parsed Molecule data
    :rtype: dict
    """
    result = {
        "id": item.id,
        "name": str(item),
        "required_quantity": 0,
        "quantity": 0,
        "allowance": [],
        "remark": item.remark,
        "picture": None,
        "contents": [],
        "type": "molecule",
        "perishable": True,
        "consumable": True,
        "has_nc": False,
        "has_date_warning": False,
        "has_date_expired": False,
        "locations": [],
        "exp_dates": []
    }

    if required:
        result["required_quantity"] = required[item.id]["maximum"] + required[item.id]["additional"]
        result["allowance"] = required[item.id]["detail"]

    return result


def create_equipment(item, required):
    """Return a dictionary of an equipment.

    :param models.Equipment item: An Equipment instance.
    :param required: Dictionary of required quantities for equipments \
    (keys are Molecule ID).

    :return: Dictionary of parsed Equipment data
    :rtype: dict
    """
    result = {
        "id": item.id,
        "name": str(item),
        "required_quantity": 0,
        "quantity": 0,
        "allowance": [],
        "remark": item.remark,
        "picture": item.picture,
        "contents": [],
        "type": "equipment",
        "perishable": item.perishable,
        "consumable": item.consumable,
        "has_nc": False,
        "has_date_warning": False,
        "has_date_expired": False,
        "locations": [],
        "exp_dates": []
    }

    if item.id in required:
        result["required_quantity"] = required[item.id]["maximum"] + required[item.id]["additional"]
        result["allowance"] = required[item.id]["detail"]

    return result


def get_medicines(params, required, location_list):
    """Get medicines in a RescueBag.

    :param object params: Global Parameters of the application \
    (:class:`pharmaship.gui.view.GlobalParameters`)
    :param dict required: Dictionary of required quantities for molecules \
    (keys are Molecule ID).
    :param list location_list: List of \
    :class:`pharmaship.inventory.models.Location` ID

    :return: Dictionary of parsed Molecules with their Medicines.
    :rtype: dict
    """
    # All medicines
    medicines = models.Medicine.objects.filter(
        location_id__in=location_list,
        used=False
        ).prefetch_related("parent", "location").order_by("location", "name", "exp_date")

    # Quantity transactions
    transactions = get_transactions(
        content_type=params.content_types["medicine"],
        items=medicines.values_list("id", flat=True)
        )

    # Compute once the warning date from warning_delay days
    warning_delay = params.setting.expire_date_warning_delay
    warning_date = params.today + datetime.timedelta(days=warning_delay)

    molecules = create_molecules(required.keys(), required)

    for item in medicines:
        # Add the molecule if not already present
        if item.parent_id not in molecules:
            molecules[item.parent_id] = create_molecule(item.parent)

        # Prepare the medicine dictionary
        item_dict = {
            "name": item.name,
            "exp_date": item.exp_date,
            "nc": {
                "composition": item.nc_composition,
                "molecule": item.nc_molecule
            },
            "quantity": 0,
            "warning": False,
            "expired": False,
            "remark": item.remark,
            "location": item.location_id
        }

        # Check dates
        molecules[item.parent_id]['exp_dates'].append(item.exp_date)
        if item.exp_date <= warning_date:
            item_dict['warning'] = True
            molecules[item.parent_id]['has_date_warning'] = True
        if item.exp_date <= params.today:
            item_dict['expired'] = True
            molecules[item.parent_id]['has_date_expired'] = True

        # Check non-conformity
        if item.nc_molecule or item.nc_composition:
            molecules[item.parent_id]['has_nc'] = True

        # Get quantity
        if item.id in transactions:
            item_dict["quantity"] += transactions[item.id]
            molecules[item.parent_id]["quantity"] += transactions[item.id]

        # Add item location to parent
        molecules[item.parent_id]["locations"].append(item.location_id)
        # Finally, add the medicine to the molecule
        molecules[item.parent_id]["contents"].append(item_dict)

    return molecules


def get_articles(params, required, location_list):
    """Get articles in a RescueBag.

    :param object params: Global Parameters of the application \
    (:class:`pharmaship.gui.view.GlobalParameters`)
    :param dict required: Dictionary of required quantities for equipments \
    (keys are Equipment ID).
    :param list location_list: List of \
    :class:`pharmaship.inventory.models.Location` ID

    :return: Dictionary of parsed Equipments with their Articles.
    :rtype: dict
    """
    # All articles
    articles = models.Article.objects.filter(
        location_id__in=location_list,
        used=False
        ).prefetch_related("parent", "location").order_by("location", "name", "exp_date")

    # Quantity transactions
    transactions = get_transactions(
        content_type=params.content_types["article"],
        items=articles.values_list("id", flat=True)
        )

    # Compute once the warning date from warning_delay days
    warning_delay = params.setting.expire_date_warning_delay
    warning_date = params.today + datetime.timedelta(days=warning_delay)

    equipments = create_equipments(required.keys(), required)

    for item in articles:
        # Add the molecule if not already present
        if item.parent_id not in equipments:
            equipments[item.parent_id] = create_equipment(item.parent, required)

        # Prepare the medicine dictionary
        item_dict = {
            "name": item.name,
            "exp_date": item.exp_date,
            "nc": {
                "packaging": item.nc_packaging
            },
            "quantity": 0,
            "warning": False,
            "expired": False,
            "remark": item.remark,
            "location": item.location_id
        }

        # Check dates
        if item.exp_date:
            equipments[item.parent_id]['exp_dates'].append(item.exp_date)
            if item.exp_date <= warning_date:
                item_dict['warning'] = True
                equipments[item.parent_id]['has_date_warning'] = True
            if item.exp_date <= params.today:
                item_dict['expired'] = True
                equipments[item.parent_id]['has_date_expired'] = True

        # Check non-conformity
        if item.nc_packaging:
            equipments[item.parent_id]['has_nc'] = True

        # Get quantity
        if item.id in transactions:
            item_dict["quantity"] += transactions[item.id]
            equipments[item.parent_id]["quantity"] += transactions[item.id]

        # Add item location to parent
        equipments[item.parent_id]["locations"].append(item.location_id)
        # Finally, add the medicine to the molecule
        equipments[item.parent_id]["contents"].append(item_dict)

    return equipments


def merge_bags(bags, molecules, equipments):
    """Merge bags into a single dictionary.

    :param django.db.models.query.QuerySet bags: List of Rescue Bags.
    :param dict molecules: Dictionary of parsed Molecules.
    :param dict equipments: Dictionary of parsed Equipments.

    :return: A dictionary of bags with their associated items, plus a \
    summary of items in all bags with required quantitites.
    :rtype: dict
    """
    result = {}
    for bag in bags:
        result[bag.id] = {
            "name": bag.name,
            "location_id": bag.location_id,
            "elements": []
        }

        for id, molecule in molecules.items():
            if bag.location_id not in molecule["locations"]:
                continue

            quantity = 0
            for item in molecule["contents"]:
                quantity += item["quantity"]

            molecule["quantity"] = quantity

            result[bag.id]["elements"].append(molecule)

        for id, equipment in equipments.items():
            if bag.location_id not in equipment["locations"]:
                continue

            quantity = 0
            for item in equipment["contents"]:
                quantity += item["quantity"]

            equipment["quantity"] = quantity

            result[bag.id]["elements"].append(equipment)

    return result
