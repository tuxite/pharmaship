# -*- coding: utf-8; -*-
"""Utility functions for model data handling."""
import copy

from pathlib import PurePath

import django.utils.text

from mptt.utils import get_cached_trees

from pharmaship.inventory import models


def get_quantity(transaction_list, item_id):
    """Get the item quantity from a transaction list.

    Transactions of type 1 ("in") or 8 ("stock count") are setters.
    Other types are decreasing the value.

    :param django.db.models.query.QuerySet transaction_list: List of \
    transactions :class:`pharmaship.inventory.models.QtyTransaction`.
    :param int item_id: ID of item

    :return: Quantity of item
    :rtype: int
    """
    result = 0
    for transaction in transaction_list:
        if transaction.object_id == item_id:
            if transaction.transaction_type in [1, 8]:
                result = transaction.value
            else:
                result -= transaction.value
    return result


def req_qty_element(element, req_qty_list):
    """Return the required quantity of an element.

    Use the allowance list and required quantities list.
    """
    # Required quantity
    maximum = [0, ]
    additional = 0
    allowance_list = []
    for item in req_qty_list:
        if item.base != element:
            continue
        if item.allowance.additional is True:
            additional += item.required_quantity
            allowance_list.append({
                "quantity": "+{0}".format(item.required_quantity),
                "name": item.allowance.name
            })
        else:
            maximum.append(item.required_quantity)
            allowance_list.append({
                "quantity": item.required_quantity,
                "name": item.allowance.name
            })
    return (additional + max(maximum)), allowance_list


def filepath(instance, filename):
    """Return a "slugified" filename using the instance name.

    The extension of the original filename is preserved.

    :param models.Equipment instance: Equipment instance
    :param str filename: Name of the file

    :return: Slugified filename from instance name and file extension.
    :rtype: str
    """
    # Keep the extension of the uploaded file
    extension = PurePath(filename).suffix

    name = django.utils.text.slugify(instance.name)  # Safer

    path = "{0}{1}".format(name, extension.lower())

    return path


def get_location_list(show_reserved=True):
    """Return a list of pseudo-serialized Locations.

    `show_reserved`: if True, show locations with id > 100.
    """
    locations = []

    location_list = models.Location.objects.all()
    roots = get_cached_trees(location_list)

    for root in roots:
        # Do not list the default location
        if root.id == 0:
            continue

        if show_reserved is False and root.id < 100:
            continue

        locations.append({
            "sequence": [root.name],
            "id": root.id,
            "parent": None,
            "rescue_bag": root.is_rescue_bag
        })

        children = root.get_children()
        if children:
            locations += location_iterator([root.name], children, root.id)

    return locations


def location_iterator(parent, items, parent_id):
    """Iterate over the Locations tree.

    `parent`: sequence of parent locations
    `items`: children to serialize
    `parent_id`: closed parent id
    """
    locations = []

    for item in items:
        sequence = copy.deepcopy(parent)
        sequence.append(item.name)

        locations.append({
            "sequence": sequence,
            "id": item.id,
            "parent": parent_id,
            "rescue_bag": item.is_rescue_bag
        })

        children = item.get_children()
        if children:
            locations += location_iterator(sequence, children, item.id)

    return locations
