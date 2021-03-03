# -*- coding: utf-8 -*-
"""Utility functions for parsing/serializing First Aid Kit related data."""
import datetime
import copy
import json

from pharmaship.core.utils import log

from pharmaship.inventory import models, utils
# from purchase.models import Item


def get_required(params):
    """Get required quantities.

    :param object params: Global Parameters of the application \
    (:class:`pharmaship.gui.view.GlobalParameters`)

    :return: A dictionary of required quantities sorted by type (molecule or \
    equipment) and subsequent item ID.
    :rtype: dict
    """
    req_qty_list = models.FirstAidKitReqQty.objects.filter(
        allowance__in=params.allowances
        ).select_related('allowance')
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


def create_molecule(item, content_type, required=None):
    """Return a dictionary of a molecule.

    :param models.Molecule item: A Molecule instance.
    :param int content_type: ContentType ID of Molecule model.
    :param required: Dictionary of required quantities for molecules \
    (keys are Molecule ID).

    :return: Dictionary of parsed Molecule data
    :rtype: dict
    """
    result = {
        "name": str(item),
        "required_quantity": 0,
        "quantity": 0,
        "expiring_quantity": 0,
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
    """Return a dictionary of an equipment.

    :param models.Equipment item: An Equipment instance.
    :param int content_type: ContentType ID of Molecule model.
    :param required: Dictionary of required quantities for equipments \
    (keys are Molecule ID).

    :return: Dictionary of parsed Equipment data
    :rtype: dict
    """
    result = {
        "name": str(item),
        "required_quantity": 0,
        "quantity": 0,
        "expiring_quantity": 0,
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
    """Get the list of available medicines (in "chest") for a given molecule.

    :param models.Molecule element: A Molecule instance
    :param int content_type_id: ContentType ID of Medicine model.
    :param dict qty_transactions: Dictionary of compiled quantities. \
    This dictionary is obtained from :py:func:`get_transactions`.

    :return: A list of available medicines for the selected molecule with \
    quantities available.
    :rtype: dict
    """
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

        if item.packing_name > 0:
            item_dict['packing'] = {
                "id": item.packing_name,
                "name": item.get_packing_name_display(),
                "content": item.packing_content
            }
        else:
            item_dict['packing'] = None

        result.append(item_dict)

    return result


def get_available_articles(element, content_type_id, qty_transactions):
    """Get the list of available articles (in "chest") for a given equipment.

    :param models.Molecule element: An Equipment instance
    :param int content_type_id: ContentType ID of Article model.
    :param dict qty_transactions: Dictionary of compiled quantities. \
    This dictionary is obtained from :py:func:`get_transactions`.

    :return: A list of available articles for the selected equipment with \
    quantities available.
    :rtype: dict
    """
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

        if item.packing_name > 0:
            item_dict['packing'] = {
                "id": item.packing_name,
                "name": item.get_packing_name_display(),
                "content": item.packing_content
            }
        else:
            item_dict['packing'] = None

        result.append(item_dict)

    return result


def subitem_nc(nc_string):
    """Return the non-conformities dict if any and flag if non-conformity."""
    result = {
        "packaging": "",
        "composition": "",
        "molecule": ""
    }
    has_nc = False

    if not nc_string:
        return (result, has_nc)

    try:
        data = json.loads(nc_string)
    except json.decoder.JSONDecodeError:
        log.exception("First Aid Kit non conformity field error.")
        log.debug(nc_string)
        return (result, has_nc)

    for field in result.keys():
        if field not in data:
            continue
        if data[field] != "":
            result[field] = data[field]
            has_nc = True

    return result, has_nc


def get_subitems(params, kit, common):
    """Get the list of items currently in a First Aid Kit instance.

    :param object params: Global Parameters of the application \
    (:class:`pharmaship.gui.view.GlobalParameters`)
    :param models.FirstAidKit kit: First Aid Kit instance.
    :param dict common: Dictionary of all parsed and available elements.

    :return: ``common`` dictionary with additional key containing the list of \
    First Aid Kit items.
    :rtype: dict
    """
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

        child["nc"], _has_nc = subitem_nc(item.nc)
        # Avoid next subitems to erase the True has_nc
        parent["has_nc"] |= _has_nc

        if item.id in qty_transactions:
            child["quantity"] = qty_transactions[item.id]
            if not child["expired"]:
                parent["quantity"] += child["quantity"]
            if child["warning"]:
                parent["expiring_quantity"] += child["quantity"]

        parent["contents"].append(child)

    return result


def merge_elements(elements_dict):
    """Merge elements of each dictionary key into a unique list.

    :param dict elements_dict: Input dictionary. It must have the following \
    keys:

      * ``molecules``
      * ``equipments``

    :return: A list of all values of the dictionary, without the keys.
    :rtype: list

    :Example:

    >>> data = {"molecules": {1: "A", 2: "B"}, "equipments": {8: "C", 9: "D"}}
    >>> merge_elements(data)
    ["A", "B", "C", "D"]
    """
    result = []

    for k, element in elements_dict["molecules"].items():
        result.append(element)

    for k, element in elements_dict["equipments"].items():
        result.append(element)

    return result


def parser(params, kits=None):
    """Parse the database to render a list of Kits with their contents.

    This function processes database data and sets flags on articles missing, \
    expired or reaching near expiry.

    It parses also the available items in "chest" according to the required \
    elements (Molecules and Equipments).

    Only elements with :class:`pharmaship.inventory.models.FirstAidKitReqQty`\
    are listed.

    See ``pharmaship/schemas/parsers/first_aid`` for details.

    Resumed architecture of the method:

        1. Get required quantities: :py:func:`get_required`
        2. Get transactions :py:func:`get_transactions`:

            * for articles of required equipments;
            * for medicines of required molecules.

        3. Parse each molecule:

            * Create the molecule dictionary: :py:func:`create_molecule`
            * Add the available medicines: :py:func:`get_available_medicines`

        3. Parse each equipment:

            * Create the equipment dictionary: :py:func:`create_equipment`
            * Add the available articles: :py:func:`get_available_articless`

        4. Create kits dictionaries:

            * Get the contents \
            (:class:`pharmaship.inventory.models.FirstAidKitItem`): \
            :py:func:`get_subitems`
            * Merge the contents: :py:func:`merge_elements`

    :param object params: Global Parameters of the application \
    (:class:`pharmaship.gui.view.GlobalParameters`)
    :param django.db.models.query.QuerySet kits: List of First Aid Kits.

    :return: Dictionnary of First Aid Kits.
    :rtype: list(dict)
    """
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
        element = create_molecule(
            item=molecule,
            content_type=params.content_types["molecule"],
            required=required["molecules"]
            )
        element["available"] = get_available_medicines(
            content_type_id=params.content_types["medicine"],
            element=molecule,
            qty_transactions=medicines_qty_transactions
            )

        common["molecules"][molecule.id] = element

    for equipment in equipment_list:
        element = create_equipment(
            item=equipment,
            content_type=params.content_types["equipment"],
            required=required["equipments"]
            )
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
