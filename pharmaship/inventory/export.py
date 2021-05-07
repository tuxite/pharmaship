# -*- coding: utf-8; -*-
"""Export methods for Inventory application."""
import tarfile
import time
import io

import hashlib

from pathlib import PurePath

from yaml import dump
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

from django.core import serializers
from django.conf import settings
from django.utils.text import slugify

from rest_framework.renderers import JSONRenderer

import pharmaship.inventory.models as models
import pharmaship.inventory.serializers

from pharmaship.core.utils import remove_yaml_pk, get_content_types
from pharmaship.core.utils import log, query_count_all


def serialize_allowance(allowance, content_types):
    """Export an allowance using the YAML format.

    To have an usable export, the user needs:

      - the :mod:`pharmaship.inventory.models.Allowance` selected instance,

    And related to this instance:

      - the :mod:`pharmaship.inventory.models.Molecule` objects list,
      - the :mod:`pharmaship.inventory.models.Equipment` objects list,
      - the :mod:`pharmaship.inventory.models.MoleculeReqQty` objects list,
      - the :mod:`pharmaship.inventory.models.EquipmentReqQty` objects list,
      - the :mod:`pharmaship.inventory.models.RescueBagReqQty` objects list,
      - the :mod:`pharmaship.inventory.models.FirstAidKitReqQty` objects list,
      - the :mod:`pharmaship.inventory.models.TelemedicalReqQty` objects list,
      - the :mod:`pharmaship.inventory.models.LaboratoryReqQty` objects list.

    This function grabs all these together in a list of tuples::

        [('filename.yaml', <yaml content string>)]


    In addition, it returns the Equipment and Molecule lists.

    :param pharmaship.inventory.models.Allowance allowance: Allowance to \
    serialize.

    :return: List of tuples filenames and streams
    :rtype: tuple(list(tuple(str, str)), django.db.models.query.QuerySet, \
    django.db.models.query.QuerySet)
    """
    log.debug("Start serialize")

    renderer = JSONRenderer()
    # Molecules used by the allowance
    molecule_id_list = []
    equipment_id_list = []

    # Required quantities for molecules
    molecule_reqqty_list = models.MoleculeReqQty.objects.filter(allowance__in=[allowance]).prefetch_related("base")
    molecule_id_list += molecule_reqqty_list.values_list("base_id", flat=True)

    serialized = pharmaship.inventory.serializers.MoleculeReqQtySerializer(molecule_reqqty_list, many=True)
    molecule_reqqty_data = renderer.render(
        data=serialized.data,
        accepted_media_type='application/json; indent=2'
        )
    query_count_all()

    # Required quantities for equipments
    equipment_reqqty_list = models.EquipmentReqQty.objects.filter(allowance__in=[allowance]).prefetch_related("base")
    equipment_id_list += equipment_reqqty_list.values_list("base_id", flat=True)

    serialized = pharmaship.inventory.serializers.EquipmentReqQtySerializer(equipment_reqqty_list, many=True)
    equipment_reqqty_data = renderer.render(
        data=serialized.data,
        accepted_media_type='application/json; indent=2'
        )
    query_count_all()

    # Required quantities for Laboratory
    laboratory_reqqty_list = models.LaboratoryReqQty.objects.filter(allowance__in=[allowance]).prefetch_related("base")
    equipment_id_list += laboratory_reqqty_list.values_list("base_id", flat=True)

    serialized = pharmaship.inventory.serializers.LaboratoryReqQtySerializer(laboratory_reqqty_list, many=True)
    laboratory_reqqty_data = renderer.render(
        data=serialized.data,
        accepted_media_type='application/json; indent=2'
        )
    query_count_all()

    # Required quantities for Telemedical
    telemedical_reqqty_list = models.TelemedicalReqQty.objects.filter(allowance__in=[allowance]).prefetch_related("base")
    equipment_id_list += telemedical_reqqty_list.values_list("base_id", flat=True)

    serialized = pharmaship.inventory.serializers.TelemedicalReqQtySerializer(telemedical_reqqty_list, many=True)
    telemedical_reqqty_data = renderer.render(
        data=serialized.data,
        accepted_media_type='application/json; indent=2'
        )
    query_count_all()

    # Required quantities for First Aid Kit
    first_aid_kit_reqqty_list = models.FirstAidKitReqQty.objects.filter(allowance__in=[allowance]).prefetch_related("base")
    molecule_id_list += first_aid_kit_reqqty_list.filter(
        content_type_id=content_types["molecule"]
        ).values_list("object_id", flat=True)
    equipment_id_list += first_aid_kit_reqqty_list.filter(
        content_type_id=content_types["equipment"]
        ).values_list("object_id", flat=True)

    serialized = pharmaship.inventory.serializers.FirstAidKitReqQtySerializer(first_aid_kit_reqqty_list, many=True)
    first_aid_kit_reqqty_data = renderer.render(
        data=serialized.data,
        accepted_media_type='application/json; indent=2'
        )
    query_count_all()

    # Required quantities for Rescue Bag
    rescue_bag_reqqty_list = models.RescueBagReqQty.objects.filter(allowance__in=[allowance]).prefetch_related("base")
    molecule_id_list += rescue_bag_reqqty_list.filter(
        content_type_id=content_types["molecule"]
        ).values_list("object_id", flat=True)
    equipment_id_list += rescue_bag_reqqty_list.filter(
        content_type_id=content_types["equipment"]
        ).values_list("object_id", flat=True)

    serialized = pharmaship.inventory.serializers.RescueBagReqQtySerializer(rescue_bag_reqqty_list, many=True)
    rescue_bag_reqqty_data = renderer.render(
        data=serialized.data,
        accepted_media_type='application/json; indent=2'
        )
    query_count_all()

    # Equipment used by the allowance
    equipment_list = models.Equipment.objects.filter(id__in=equipment_id_list).prefetch_related("group")
    equipment_data = serializers.serialize(
        "yaml",
        equipment_list,
        use_natural_foreign_keys=True,
        fields=(
            "name_en",
            "packaging_en",
            "remark_en",
            "consumable",
            "perishable",
            "picture",
            "group",
            )
        )
    log.debug("Equipment")
    query_count_all()

    # Molecule used by the allowance
    molecule_list = models.Molecule.objects.filter(id__in=molecule_id_list).prefetch_related("group")
    molecule_data = serializers.serialize(
        "yaml",
        molecule_list,
        use_natural_foreign_keys=True,
        fields=(
            "name_en",
            "composition_en",
            "remark_en",
            "roa",
            "dosage_form",
            "medicine_list",
            "group",
            )
        )
    log.debug("Molecule")
    query_count_all()

    # Allowance record
    allowance_data = serializers.serialize(
        "yaml",
        (allowance,),
        fields=('name', 'author', 'version', 'date', 'additional'),
        use_natural_foreign_keys=True
        )
    log.debug("Allowance")
    query_count_all()

    log.debug("End serialize")

    # Returning a list with tuples: (filename, data)
    return ([
        ('inventory/molecule_obj.yaml', remove_yaml_pk(molecule_data)),
        ('inventory/equipment_obj.yaml', remove_yaml_pk(equipment_data)),

        ('inventory/molecule_reqqty.json', molecule_reqqty_data),
        ('inventory/equipment_reqqty.json', equipment_reqqty_data),

        ('inventory/laboratory_reqqty.json', laboratory_reqqty_data),
        ('inventory/telemedical_reqqty.json', telemedical_reqqty_data),

        ('inventory/first_aid_kit_reqqty.json', first_aid_kit_reqqty_data),
        ('inventory/rescue_bag_reqqty.json', rescue_bag_reqqty_data),

        ('inventory/allowance.yaml', remove_yaml_pk(allowance_data)),
    ], equipment_list, molecule_list)


def get_pictures(equipment_list):
    """Return a list of picture paths to include in the archive.

    :param equipment_list: List of equipment for serialized allowance.
    :type equipment_list: django.db.models.query.QuerySet

    :return: List of pictures filenames.
    :rtype: list
    """
    # Pictures attached to equipments
    pictures = equipment_list.exclude(picture='').values_list(
        'picture', flat=True)

    return pictures


def get_hash(name, content=None, filename=None):
    """Return sha256 hash and filename for MANIFEST file.

    :param str name: Name of the file to hash.
    :param content: Content of the file to hash.
    :type content: bytes or str
    :param str filename: Path to the file to hash.

    :return: Name and file hash in hexadecimal string.
    :rtype: tuple(str, str)
    """
    if content is None and filename is None:
        return None

    m = hashlib.sha256()
    if content:
        if isinstance(content, bytes):
            m.update(content)
        else:
            m.update(bytes(content, "utf-8"))
    elif filename:
        try:
            with open(filename, 'rb') as fdesc:
                m.update(fdesc.read())
        except IOError as error:
            log.error("File %s not readable. %s", filename, error)
            return None

    return (name, m.hexdigest())


def create_tarinfo(name, content):
    """Return a the TarInfo for a virtual file.

    :param str name: Name of the file
    :param content: Content of the file to add to the tar file.
    :type content: bytes or str

    :return: :class:`tarfile.TarInfo` and :class:`io.BytesIO` instance of the
             file content.
    :rtype: tuple
    """
    if isinstance(content, bytes):
        f = io.BytesIO(content)
    else:
        f = io.BytesIO(bytes(content, "utf-8"))
    info = tarfile.TarInfo()
    info.name = name
    info.type = tarfile.REGTYPE
    info.uid = info.gid = 0
    info.uname = info.gname = "root"
    info.mtime = time.time()
    info.size = len(f.getvalue())

    return (info, f)


def create_manifest(items):
    """Create the data to write into the MANIFEST file.

    :param list(tuple) items: list of files with their hash.

    :return: Formatted string
    :rtype: str
    """
    content = ""
    for item in items:
        content += "{1}  {0}\n".format(item[0], item[1])

    return content


def create_package_yaml(allowance):
    """Export package info in YAML string.

    :param allowance: Allowance instance to export
    :type allowance: pharmaship.inventory.models.Allowance

    :return: YAML string containing Allowance data.
    :rtype: str
    """
    content = {
        "info": {
            "author": allowance.author,
            "date": allowance.date,
            "version": allowance.version
        },
        "modules": {
            "inventory": {
                "install_file": False
            }
        }
    }
    content_string = dump(content, Dumper=Dumper)

    return content_string


def create_pot(allowance):
    """Create of PO template file for Equipment & Molecule strings."""
    # Get serialized Allowance data
    content_types = get_content_types()
    _data, equipment_list, molecule_list = serialize_allowance(allowance, content_types)

    strings = []
    for item in equipment_list:
        strings.append(item.name)
        strings.append(item.packaging)
        strings.append(item.remark)
    for item in molecule_list:
        strings.append(item.name)
        strings.append(item.remark)

    # Remove empty strings
    strings = list(filter(None, strings))
    # Remove duplicates
    strings = list(set(strings))
    # Sort for easier translation
    strings.sort()

    # Create POT file
    result = """msgid ""
msgstr ""
"Project-Id-Version: Pharmaship export\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"\n
"""
    for item in strings:
        result += "msgid \"{0}\"\n".format(item.replace("\"", "\\\""))
        result += "msgstr \"\"\n\n"
    return result


def create_po(allowance, lang_code):
    # Get serialized Allowance data
    content_types = get_content_types()
    _data, equipment_list, molecule_list = serialize_allowance(allowance, content_types)

    strings = {}
    for item in equipment_list:
        strings[item.name_en] = getattr(item, "name_{0}".format(lang_code))
        strings[item.packaging_en] = getattr(item, "packaging_{0}".format(lang_code))
        strings[item.remark_en] = getattr(item, "remark_{0}".format(lang_code))
    for item in molecule_list:
        strings[item.name_en] = getattr(item, "name_{0}".format(lang_code))
        strings[item.composition_en] = getattr(item, "composition_{0}".format(lang_code))
        strings[item.remark_en] = getattr(item, "remark_{0}".format(lang_code))

    # Create PO file
    result = """msgid ""
msgstr ""
"Project-Id-Version: Pharmaship export\\n"
"MIME-Version: 1.0\\n"
"Language: {0}\\n"
"Plural-Forms: nplurals=2; plural=(n != 1)\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"\n
""".format(lang_code.lower())
    for item in strings:
        if not item:
            continue
        result += "msgid \"{0}\"\n".format(item.replace("\"", "\\\""))
        result += "msgstr \"{0}\"\n\n".format(strings[item].replace("\"", "\\\""))
    return result


def create_archive(allowance, file_obj):
    """Create an archive from the given `Allowance` instance.

    The response is a tar.gz file containing YAML files generated by the
    function `serialize_allowance`.

    Pictures are added if any.

    The package description file (``package.yaml``) and the ``MANIFEST`` file
    are created at the end.

    :param allowance: Allowance instance to export
    :type allowance: pharmaship.inventory.models.Allowance
    :param file_obj: Destination file object
    :type file_obj: argparse.FileType or any compatible file object

    :return: ``True`` if success
    :rtype: bool
    """
    # Creating a tar.gz archive
    hashes = []

    serialized_data, equipment_list, molecule_list = serialize_allowance(
        allowance=allowance,
        content_types=get_content_types()
        )

    with tarfile.open(fileobj=file_obj, mode='w') as tar:
        # Processing the database
        for item in serialized_data:
            info, f = create_tarinfo(item[0], item[1])
            tar.addfile(info, f)

            hashes.append(get_hash(info.name, content=item[1]))

        # Adding the pictures of Equipment
        for item in get_pictures(equipment_list):
            picture_filename = settings.PICTURES_FOLDER / item
            log.debug(picture_filename)
            try:
                tar.add(picture_filename, arcname=PurePath("pictures", item))
            # TODO: Detail Exception
            except Exception as error:
                log.error("Error: %s", error)

            hashes.append(
                get_hash(PurePath("pictures", item), filename=picture_filename)
                )

        # Adding the translation files if any
        # TODO: Generate MO if only PO is found...
        mo_filename = "{0}.mo".format(slugify(allowance.name))
        for item in settings.TRANSLATIONS_FOLDER.glob("*/LC_MESSAGES/{0}".format(mo_filename)):
            log.debug(item)
            relative_path = PurePath("locale", item.relative_to(settings.TRANSLATIONS_FOLDER))
            tar.add(item, arcname=relative_path)
            hashes.append(get_hash(relative_path, filename=item))
            # Try to get also the PO file
            po_filename = item.with_suffix(".po")
            if po_filename.exists():
                log.debug(po_filename)
                relative_path = PurePath("locale", po_filename.relative_to(settings.TRANSLATIONS_FOLDER))
                tar.add(po_filename, arcname=relative_path)
                hashes.append(get_hash(relative_path, filename=po_filename))


        # Add the package description file
        package_content = create_package_yaml(allowance)
        info, f = create_tarinfo("package.yaml", package_content)
        tar.addfile(info, f)
        hashes.append(get_hash("package.yaml", content=package_content))

        # Add the MANIFEST
        manifest_content = create_manifest(hashes)
        info, f = create_tarinfo("MANIFEST", manifest_content)
        tar.addfile(info, f)

    return True
