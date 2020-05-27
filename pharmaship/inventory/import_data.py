# -*- coding: utf-8; -*-
"""Import methods for Inventory application."""
import os.path
import json

from django.utils.translation import ugettext as _
from django.core import serializers as core_serializers
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from pharmaship.inventory import models
from pharmaship.inventory import serializers

from pharmaship.core.utils import log, query_count_all


def pictures_files(members):
    for tarinfo in members:
        path_strings = os.path.split(tarinfo.name)
        if path_strings[0] == "pictures":
            # Modify the path of the picture to manage later the full path
            tarinfo.name = path_strings[1]
            yield tarinfo


def update_allowance(allowance, key):
    log.debug("Allowance name: %s", allowance.name)

    allowance_dict = allowance.__dict__
    allowance_dict.pop('id', None)
    allowance_dict.pop('_state', None)
    allowance_dict['signature'] = key
    # Unique: (name, )
    obj, created = models.Allowance.objects.update_or_create(
        name=allowance.name,
        defaults=allowance_dict
    )
    if not created:
        log.info("Allowance `%s` already exists, updated.", allowance.name)
    else:
        log.info("Allowance `%s` create.", allowance.name)

    return obj


def get_file(filename, tar):
    """Extract `filename` from `tar` file."""
    try:
        fdesc = tar.extractfile(filename)
    except KeyError:
        log.error("File `%s` not found.", filename)
        return False

    return fdesc.read()


def get_model(data):
    try:
        ct = ContentType.objects.get_by_natural_key(
            app_label=data["app_label"],
            model=data["name"]
        )
    except ContentType.objects.DoesNotExist:
        log.error("ContentType not found.")
        log.debug(data)
        return None
    return ct


def get_base(type, content, model=None):
    if not model:
        model = type.field.related_model
    instance = model.objects.get_by_natural_key(**content)
    return instance


def deserialize_json_file(data, tar, allowance):
    content = get_file(data["filename"], tar)
    if not content:
        return False

    item_data = json.loads(content)

    objects = []
    for item in item_data:
        if "content_type" not in item:
            base = get_base(
                type=data["model"].base,
                content=item["base"]
                )
        else:
            ct = get_model(item["content_type"])
            if ct is None:
                return False
            base = get_base(
                type=data["model"].base,
                content=item["base"],
                model=ct.model_class()
                )

        instance = data["model"](
            allowance=allowance,
            base=base,
            required_quantity=item["required_quantity"]
            )

        objects.append(instance)

    return objects


def required_quantity(data, tar, allowance):
    log.debug("Updating required quantities for %s", data["filename"])
    # deserialized_list = deserialize_file(data["filename"], tar)
    deserialized_list = deserialize_json_file(data, tar, allowance)

    if deserialized_list is False:
        log.error("Error when deserializing file: %", data["filename"])
        return False

    # As we are sure that the deserialization went fine,
    # delete all required quantities entry and create new ones
    data["model"].objects.filter(
        allowance_id__in=(0, allowance.id)
        ).delete()

    data["model"].objects.bulk_create(deserialized_list)
    log.debug("Created %s instances", len(deserialized_list))
    query_count_all()

    return True


class DataImport:
    """Class to import allowance inside the inventory module."""

    def __init__(self, tar, conf, key):
        self.tar = tar
        self.conf = conf
        self.key = key
        self.data = []
        self.module_name = __name__.split('.')[-2]

    def import_allowance(self):
        content = get_file("inventory/allowance.yaml", self.tar)
        if not content:
            return False

        deserialized_allowance = core_serializers.deserialize("yaml", content)

        for allowance in deserialized_allowance:
            obj = update_allowance(allowance.object, self.key['keyid'][-8:])
            break  # FUTURE: Only one allowance per file?

        return obj

    def import_molecule(self):
        content = get_file("inventory/molecule_obj.yaml", self.tar)
        if not content:
            return False

        deserialized_list = core_serializers.deserialize("yaml", content)

        for molecule in deserialized_list:
            # Unique: (name, roa, dosage_form, composition)
            unique_values = {
                'name': molecule.object.name,
                'roa': molecule.object.roa,
                'dosage_form': molecule.object.dosage_form,
                'composition': molecule.object.composition,
            }
            molecule_dict = dict(unique_values)  # Hard copy
            molecule_dict['medicine_list'] = molecule.object.medicine_list
            molecule_dict['group'] = molecule.object.group
            molecule_dict['remark'] = molecule.object.remark

            # TODO: DB calls optimization
            obj, created = models.Molecule.objects.update_or_create(
                defaults=molecule_dict,
                **unique_values
            )
            # Add M2M relations
            try:
                if molecule.m2m_data['tag']:
                    obj.tag = molecule.m2m_data['tag']
                    obj.save()
            except KeyError:
                pass

            if created:
                log.debug("Created molecule: %s", obj)

        return True

    def import_equipment(self):
        content = get_file("inventory/equipment_obj.yaml", self.tar)
        if not content:
            return False

        deserialized_list = core_serializers.deserialize("yaml", content)

        for equipment in deserialized_list:
            # Unique: (name, packaging, perishable, consumable)
            unique_values = {
                'name': equipment.object.name,
                'packaging': equipment.object.packaging,
                'perishable': equipment.object.perishable,
                'consumable': equipment.object.consumable
            }
            equipment_dict = dict(unique_values)  # Hard copy
            equipment_dict["group"] = equipment.object.group
            equipment_dict['picture'] = equipment.object.picture
            equipment_dict['remark'] = equipment.object.remark

            # TODO: DB calls optimization
            obj, created = models.Equipment.objects.update_or_create(
                defaults=equipment_dict,
                **unique_values
            )

            if created:
                log.debug("Created equipment: %s", obj)

        return True

    def update(self):
        """Launch the importation.

        :model:`Molecule` and :mod:`Equipment` objects with
        no allowance (orphan) are stored for further treatment.
        :model:`Molecule` and :mod:`Equipment` are updated
        or added (if their pk cannot be determined).

        :model:`Allowance` object is updated or created by the
        same process.

        :model:`MoleculeReqQty` and
        :model:`EquipmentReqQty` are erased for the allowance
        and re-created.

        Finally, the new orphan molecules are affected to a special
        allowance with 0 as required quantity.
        """
        log.info("Inventory import...")

        # Detecting objects without allowance (orphan)
        self.no_allowance = models.Allowance.objects.get(pk=0)
        query_count_all()
        self.files = self.tar.getnames()

        allowance = self.import_allowance()
        if not allowance:
            return False
        query_count_all()

        if not self.import_molecule():
            return False
        query_count_all()

        if not self.import_equipment():
            return False
        query_count_all()

        # Required Quantities
        required = [
            {
                "filename": "inventory/molecule_reqqty.json",
                "model": models.MoleculeReqQty,
                "serializer": serializers.MoleculeReqQtySerializer
            },
            {
                "filename": "inventory/equipment_reqqty.json",
                "model": models.EquipmentReqQty,
                "serializer": serializers.EquipmentReqQtySerializer
            },
            {
                "filename": "inventory/telemedical_reqqty.json",
                "model": models.TelemedicalReqQty,
                "serializer": serializers.TelemedicalReqQtySerializer
            },
            {
                "filename": "inventory/laboratory_reqqty.json",
                "model": models.LaboratoryReqQty,
                "serializer": serializers.LaboratoryReqQtySerializer
            },
            {
                "filename": "inventory/rescue_bag_reqqty.json",
                "model": models.RescueBagReqQty,
                "serializer": serializers.RescueBagReqQtySerializer
            },
            {
                "filename": "inventory/first_aid_kit_reqqty.json",
                "model": models.FirstAidKitReqQty,
                "serializer": serializers.FirstAidKitReqQtySerializer
            },
        ]

        query_count_all()

        for item in required:
            res = required_quantity(item, self.tar, allowance)
            if not res:
                return False

        # Listing molecules with no reqqty
        molecule_orphan_after = models.Molecule.objects.filter(
            allowances=None)
        equipment_orphan_after = models.Equipment.objects.filter(
            allowances=None)

        log.info("Orphan Molecules: %s", len(molecule_orphan_after))
        log.info("Orphan Equipments: %s", len(equipment_orphan_after))

        # Creating reqqty with special allowance (id=1)
        for molecule in molecule_orphan_after:
            models.MoleculeReqQty.objects.create(
                base=molecule,
                allowance=self.no_allowance,
                required_quantity=0
                )

        for equipment in equipment_orphan_after:
            models.EquipmentReqQty.objects.create(
                base=equipment,
                allowance=self.no_allowance,
                required_quantity=0
                )

        # Copying pictures
        self.tar.extractall(
            members=pictures_files(self.tar),
            path=str(settings.PICTURES_FOLDER)
            )

        # Set allowance active as everything went well
        allowance.active = True
        allowance.save()

        return True
