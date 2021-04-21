# -*- coding: utf-8; -*-
"""Import methods for Inventory application."""
# import os.path
import json

from pathlib import PurePath

from django.core import serializers
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from pharmaship.inventory import models
# from pharmaship.inventory import serializers

from pharmaship.core.utils import log, query_count_all


def pictures_files(members):
    """Change the picture path in TarInfo instance.

    :param list(tarfile.TarInfo) members: files in the tar file.

    :return: An iterator with tar file members containing ``pictures`` as\
    first path part.
    """
    for tarinfo in members:
        path_strings = PurePath(tarinfo.name).parts
        if len(path_strings) < 2:
            continue

        if path_strings[0] == "pictures":
            # Modify the path of the picture to manage later the full path
            tarinfo.name = path_strings[1]
            yield tarinfo


def update_allowance(allowance, key):
    """Update or create an allowance instance from serialized allowance data.

    :param models.Allowance allowance: Up-to-date Allowance instance.
    :param str key: GPG key ID used for signing the package archive.

    :return: the updated (or create) allowance instance
    :rtype: models.Allowance
    """
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
    """Extract a file from a tar archive.

    :param str filename: Filename to extract from tar file.
    :param tarfile.TarFile tar: tar file instance.

    :return: Content of the file or ``False`` if the file cannot be accessed.
    :rtype: bytes or bool
    """
    try:
        fdesc = tar.extractfile(filename)
    except KeyError:
        log.error("File `%s` not found.", filename)
        return False

    return fdesc.read()


def get_model(data):
    """Return the related ContentType from `data`.

    :param dict data: Dictionnary containing at least following keys:

      * ``app_label``: the application name,
      * ``name``: the name of the model

    :return: The Django ContentType instance or ``None`` if it does not exist.
    :rtype: django.contrib.contenttypes.models.ContentType or None
    """
    try:
        ct = ContentType.objects.get_by_natural_key(
            app_label=data["app_label"],
            model=data["name"]
        )
    except ContentType.DoesNotExist:
        log.error("ContentType not found.")
        log.debug(data)
        return None
    return ct


def get_base(type, content, model=None):
    """Return a model instance according to the type and model if provided.

    If the `model` is not provided, it is retrieved from the `type` structure.
    On some `model` (ie: :mod:`pharmaship.inventory.models.RescueBagReqQty`),
    the type can be either :mod:`pharmaship.inventory.models.Equipment` or
    :mod:`pharmaship.inventory.models.Molecule`.

    :param type: Model class of base field (Django internal).
    :type type: models.Equipment or models.Molecule
    :param dict content: Dictionnary with all natural key fields for the\
    related base.
    :param model: Model class of base item to serialize.
    :type model: models.Equipment or models.Molecule

    :return: A model instance or ``None`` if not found.
    :rtype: models.Equipment or models.Molecule or None
    """
    if not model:
        try:
            model = type.field.related_model
        except AttributeError as error:
            log.error("Model class not found: %s", error)
            return None
    try:
        instance = model.objects.get_by_natural_key(**content)
    except model.DoesNotExist:
        log.error("%s instance does not exist.", model)
        log.debug(content)
        return None
    return instance


def deserialize_json_file(data, tar, allowance):
    """Deserialize a JSON file contained in the tar file.

    :param dict data: Dictionnary with filename and model related. The \
    following keys must be present:

      * ``filename``: the name of the JSON file to extract from the tar \
      archive;
      * ``model``: the class of model to deserialize \
      (ie: :mod:`pharmaship.inventory.models.MoleculeReqQty`).

    :param tarfile.TarFile tar: tar file archive containing the file to extract
    :param allowance: allowance instance to rattach
    :type allowance: models.Allowance

    :return: List of `model` instances.
    :rtype: list
    """
    content = get_file(data["filename"], tar)
    if not content:
        return False

    try:
        item_data = json.loads(content)
    except json.decoder.JSONDecodeError as error:
        log.error("Corrupted JSON file: %s", error)
        return False

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

        if not base:
            log.error("Base for item not found.")
            log.debug(item)
            return False

        instance = data["model"](
            allowance=allowance,
            base=base,
            required_quantity=item["required_quantity"]
            )

        objects.append(instance)

    return objects


def required_quantity(data, tar, allowance):
    """Update the required quantities for deserialized items.

    After successful deserialization, delete all related required quantity for
    the selected allowance. Then create all deserialized objects.

    :param dict data: Dictionnary with filename and model related. The \
    following keys must be present:

      * ``filename``: the name of the JSON file to extract from the tar \
      archive;
      * ``model``: the class of model to deserialize \
      (ie: :mod:`pharmaship.inventory.models.MoleculeReqQty`).

    :param tarfile.TarFile tar: tar file archive containing the file to extract
    :param allowance: allowance instance to rattach
    :type allowance: models.Allowance

    :return: ``True`` if there is no error, ``False`` otherwise.
    :rtype: bool
    """
    log.debug("Updating required quantities for %s", data["filename"])

    deserialized_list = deserialize_json_file(data, tar, allowance)

    if deserialized_list is False:
        log.error("Error when deserializing file: %s", data["filename"])
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
    """Class to import allowance inside the inventory module.

    :param tarfile.TarFile tar: Tarfile data to import.
    :param dict conf: Validated package configuration (not used).
    :param dict key: GPG key data used for signing the package archive.
    """

    def __init__(self, tar, conf, key):  # noqa: D107
        self.tar = tar
        self.key = key
        self.data = []
        self.module_name = __name__.split('.')[-2]

    def import_allowance(self):
        """Import an Allowance from a YAML file.

        Update the :mod:`pharmaship.inventory.models.Allowance` info or
        create it from scratch.

        :return: Allowance instance or ``False`` in case of import error.
        :rtype: models.Allowance or bool
        """
        content = get_file("inventory/allowance.yaml", self.tar)
        if not content:
            return False

        try:
            deserialized_allowance = serializers.deserialize("yaml", content)
            deserialized_allowance = list(deserialized_allowance)
        except serializers.base.DeserializationError as error:
            log.error("Cannot deserialize allowance: %s", error)
            return False

        for allowance in deserialized_allowance:
            obj = update_allowance(allowance.object, self.key['keyid'][-8:])
            break  # FUTURE: Only one allowance per file?

        return obj

    def import_molecule(self):
        """Import Molecule objects from a YAML file.

        Use Django's update_or_create method for
        :mod:`pharmaship.inventory.models.Molecule`.

        :return: ``True`` if successful import, ``False`` otherwise.
        :rtype: bool
        """
        content = get_file("inventory/molecule_obj.yaml", self.tar)
        if not content:
            return False

        try:
            deserialized_list = serializers.deserialize("yaml", content)
            deserialized_list = list(deserialized_list)
        except serializers.base.DeserializationError as error:
            log.error("Cannot deserialize molecule objects: %s", error)
            return False

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
        """Import Equipment objects from a YAML file.

        Use Django's update_or_create method for
        :mod:`pharmaship.inventory.models.Equipment`.

        :return: ``True`` if successful import, ``False`` otherwise.
        :rtype: bool
        """
        content = get_file("inventory/equipment_obj.yaml", self.tar)
        if not content:
            return False

        try:
            deserialized_list = serializers.deserialize("yaml", content)
            deserialized_list = list(deserialized_list)
        except serializers.base.DeserializationError as error:
            log.error("Cannot deserialize equipment objects: %s", error)
            return False

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

        Import first the :mod:`pharmaship.inventory.models.Allowance`.
        Then, import all :mod:`pharmaship.inventory.models.Molecule` and
        :mod:`pharmaship.inventory.models.Equipment` objects (update or
        create them).

        When this is done, parse each JSON file for required quantities:

        * :mod:`pharmaship.inventory.models.MoleculeReqQty`
        * :mod:`pharmaship.inventory.models.EquipmentReqQty`
        * :mod:`pharmaship.inventory.models.RescueBagReqQty`
        * :mod:`pharmaship.inventory.models.FirstAidKitReqQty`
        * :mod:`pharmaship.inventory.models.LaboratoryReqQty`
        * :mod:`pharmaship.inventory.models.TelemedicalReqQty`

        :mod:`pharmaship.inventory.models.Molecule` and
        :mod:`pharmaship.inventory.models.Equipment` objects without
        required quantity after import are affected to the default
        :mod:`pharmaship.inventory.models.Allowance` (``id=0``) with a
        required quantity of 0.

        :return: ``True`` if import successful, ``False`` otherwise.
        :rtype: bool
        """
        log.info("Inventory import...")

        # Detecting objects without allowance (orphan)
        self.no_allowance = models.Allowance.objects.get(pk=0)
        query_count_all()

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
                # "serializer": serializers.MoleculeReqQtySerializer
            },
            {
                "filename": "inventory/equipment_reqqty.json",
                "model": models.EquipmentReqQty,
                # "serializer": serializers.EquipmentReqQtySerializer
            },
            {
                "filename": "inventory/telemedical_reqqty.json",
                "model": models.TelemedicalReqQty,
                # "serializer": serializers.TelemedicalReqQtySerializer
            },
            {
                "filename": "inventory/laboratory_reqqty.json",
                "model": models.LaboratoryReqQty,
                # "serializer": serializers.LaboratoryReqQtySerializer
            },
            {
                "filename": "inventory/rescue_bag_reqqty.json",
                "model": models.RescueBagReqQty,
                # "serializer": serializers.RescueBagReqQtySerializer
            },
            {
                "filename": "inventory/first_aid_kit_reqqty.json",
                "model": models.FirstAidKitReqQty,
                # "serializer": serializers.FirstAidKitReqQtySerializer
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
