# -*- coding: utf-8 -*-
import datetime
import locale

from django.utils.translation import gettext as _

from pharmaship.core.utils import log

from pharmaship.inventory import models
from pharmaship.inventory.utils import req_qty_element, get_quantity
# from purchase.models import Item


# Pre-treatment function
def parser(params):
    """Parse the database to render a dict of MoleculeGroup/Molecule/Medicine.

    Process database data and set flags on medicines missing, expired or \
    reaching near expiry.

    Only molecules with :class:`pharmaship.inventory.models.MoleculeReqQty` \
    are listed.

    Data is sorted by :class:`pharmaship.inventory.models.MoleculeGroup`.

    See ``pharmaship/schemas/parsers/medicines.json`` for details.

    :param object params: Global Parameters of the application \
    (:class:`pharmaship.gui.view.GlobalParameters`)

    :return: Dictionnary with list of Molecule by MoleculeGroup.
    :rtype: dict(list)
    """
    data = {}
    allowance_list = params.allowances
    location_list = params.locations
    warning_delay = params.setting.expire_date_warning_delay
    today = params.today
    # Required quantities for listed allowances
    req_qty_list = models.MoleculeReqQty.objects.filter(allowance__in=allowance_list).prefetch_related('base', 'allowance')
    # Molecule list
    molecules = models.Molecule.objects.filter(allowances__in=allowance_list).distinct().prefetch_related('group', 'tag', 'medicines').order_by('group', 'name')
    # Medicine quantity transaction list
    data["qty_transactions"] = models.QtyTransaction.objects.filter(content_type=params.content_types['medicine']).order_by("date")

    # Ordered items
    # data["ordered_items"] = Item.objects.filter(
    #     content_type=ContentType.objects.get_for_model(models.Molecule),
    #     requisition__status__in=[4,5])

    # Locations
    data["locations"] = location_list

    if today is None:
        today = datetime.date.today()

    result = {}

    for molecule in molecules:
        element = parser_element(molecule, data, warning_delay, today)
        element["required_quantity"], element["allowance"] = req_qty_element(molecule, req_qty_list)
        # Do not add not required elemments with zero quantity
        if element["required_quantity"] == 0 and element["quantity"] == 0:
            continue

        if molecule.group not in result:
            result[molecule.group] = []

        result[molecule.group].append(element)

    for group in result:
        result[group] = sorted(
            result[group],
            key=lambda item: locale.strxfrm(item["name"])
            )

    return result


def parser_element(molecule, data, warning_delay, today):
    """Parse the database to render a list of Molecule > Medicine.

    :param models.Molecule molecule: Molecule to parse
    :param dict data: Common data for parsing. Following keys must be present:

        * ``qty_transactions``: QuerySet of \
        :class:`pharmaship.inventory.models.QtyTransaction`
        * ``locations``: formatted list of \
        :class:`pharmaship.inventory.models.Location`

    :param datetime.date warning_delay: Date from which warning flag must be \
    set
    :param datetime.date today: Date from which expired flag must be set.

    :return: Formatted information with medicines.
    :rtype: dict
    """
    # ordered_items = data["ordered_items"]
    qty_transactions = data["qty_transactions"]
    locations = data["locations"]

    element_dict = {}
    # ID
    element_dict['id'] = molecule.id
    # Name
    element_dict['name'] = molecule.name
    # Roa, Dosage_form, Composition
    element_dict['roa'] = molecule.get_roa_display()
    element_dict['dosage_form'] = molecule.get_dosage_form_display()
    element_dict['composition'] = molecule.composition

    element_dict['locations'] = []
    # Medicine_list
    if molecule.medicine_list:
        element_dict['medicine_list'] = molecule.get_medicine_list_display()
    # Remark
    element_dict['remark'] = molecule.remark
    # Ordered
    # element_dict['ordered'] = 0
    # for item in ordered_items:
    #     if item.object_id == molecule.id:
    #         element_dict['ordered'] += item.quantity
    # Tags
    element_dict['tag'] = molecule.tag
    # Quantity
    element_dict['quantity'] = 0
    element_dict['expiring_quantity'] = 0

    element_dict['medicines'] = []
    element_dict['exp_dates'] = []

    element_dict['has_nc'] = False
    element_dict['has_date_warning'] = False
    element_dict['has_date_expired'] = False

    # Compute once the warning date from warning_delay days
    warning_date = today + datetime.timedelta(days=warning_delay)

    # Create the molecule name
    molecule_name_string = "{name} ({dosage_form} - {composition})".format(**element_dict)
    # Finding attached medicines (Medicine)
    for medicine in molecule.medicines.all():
        # Do not parse the used medicines (quantity = 0)
        if medicine.used:
            continue
        item_dict = {}
        # ID
        item_dict['id'] = medicine.id
        # Name
        item_dict['name'] = medicine.name
        # Non conformity fields
        item_dict['nc_composition'] = medicine.nc_composition
        item_dict['nc_molecule'] = medicine.nc_molecule
        # Expiration date
        item_dict['exp_date'] = medicine.exp_date
        element_dict['exp_dates'].append(medicine.exp_date)
        # Check if the medicine is expired or not and if the expiry is within
        # the user-defined period
        # Consider "today" as already passed (that is why we use <= operator)
        item_dict['expired'] = False
        item_dict['warning'] = False
        if medicine.exp_date <= warning_date:
            item_dict['warning'] = True
            element_dict['has_date_warning'] = True
        if medicine.exp_date <= today:
            item_dict['expired'] = True
            element_dict['has_date_expired'] = True
        # Location

        # In case of unassigned location
        if medicine.location_id == 0:
            item_dict['location'] = {
                "sequence": [_("Unassigned")],
                "id": None,
                "parent": None,
                "rescue_bag": None
            }
            location_display = _("Unassigned")
        else:
            for item in locations:
                if medicine.location_id == item["id"]:
                    item_dict['location'] = item
                    location_display = " > ".join(item["sequence"])
                    if location_display not in element_dict['locations']:
                        element_dict['locations'].append(location_display)
        # Quantity
        item_dict['quantity'] = get_quantity(qty_transactions, medicine.id)

        if item_dict['quantity'] < 0:
            log.warning("Medicine (ID: %s) with negative quantity (%s)", item_dict["id"], item_dict["quantity"])

        # Adding the medicine quantity to the molecule quantity
        if not item_dict['expired']:
            element_dict['quantity'] += item_dict['quantity']
            if item_dict['warning']:
                element_dict['expiring_quantity'] += item_dict['quantity']

        # Add the molecule_id in case of reverse search
        item_dict['molecule'] = {
            "id": molecule.id,
            "name": molecule_name_string,
            "dosage_form": molecule.get_dosage_form_display()
            }

        # Packing
        if medicine.packing_name > 0:
            item_dict['packing'] = {
                "id": medicine.packing_name,
                "name": medicine.get_packing_name_display(),
                "content": medicine.packing_content
            }
        else:
            item_dict['packing'] = None

        # Remark
        item_dict['remark'] = medicine.remark

        # Adding the medicine dict to the list
        element_dict['medicines'].append(item_dict)

        # If medicine has a non-conformity, set element_dict.has_nc to True
        if medicine.nc_composition or medicine.nc_molecule:
            element_dict["has_nc"] = True

    # Returning the result dictionnary
    return element_dict
