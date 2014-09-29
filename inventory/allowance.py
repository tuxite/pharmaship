# -*- coding: utf-8; -*-
#
# (c) 2013 Association DSM, http://devmaretique.com
#
# This file is part of Pharmaship.
#
# Pharmaship is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# any later version.
#
# Pharmaship is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pharmaship.  If not, see <http://www.gnu.org/licenses/>.
#
# ======================================================================
# Filename:    settings/allowance.py
# Description: Functions dedicated to Allowances checks and integration.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

import tarfile, time, datetime
import xml.dom.minidom
import gpgme, os
import io, ConfigParser

from django.core import serializers
from django.http import HttpResponse
from django.conf import settings

import models

MANIFEST = [
    'info',
    'molecule_obj.xml',
    'molecule_reqqty.xml',
    'equipment_obj.xml',
    'equipment_reqqty.xml',
    'allowance.xml',
    ]

def remove_pk(xml_string):
    """Removes the PK attributes to the serialized objects.

    This allows to import different alllowances with for instance the
    same molecules without generating conflicts of primary key.
    """
    dom = xml.dom.minidom.parseString(xml_string)
    for node in dom.getElementsByTagName('object'):
        if node.hasAttribute("pk"):
            node.removeAttribute("pk")
    return dom.toxml("utf-8")

def get_molecule_pk(deserialized_object):
    """Returns the pk of a Molecule object with deserialized_object attributes."""
    # Unique: (name, roa, dosage_form, composition)
    try:
        obj = models.Molecule.objects.get(
            name = deserialized_object.object.name,
            roa = deserialized_object.object.roa,
            dosage_form = deserialized_object.object.dosage_form,
            composition = deserialized_object.object.composition,
            )
        return obj.pk
    except:
        return None

def get_equipment_pk(deserialized_object):
    """Returns the pk of an Equipment object with deserialized_object attributes."""
    # Unique: (name, packaging, perishable, consumable, group)
    try:
        obj = models.Equipment.objects.get(
            name = deserialized_object.object.name,
            packaging = deserialized_object.object.packaging,
            perishable = deserialized_object.object.perishable,
            consumable = deserialized_object.object.consumable,
            group = deserialized_object.object.group,
            )
        return obj.pk
    except:
        return None
        
def get_allowance_pk(deserialized_object):
    """Returns the pk of an Allowance object with deserialized_object attributes."""
    try:
        obj = models.Allowance.objects.get(
            name = deserialized_object.object.name,
            )
        return obj.pk
    except:
        return None

def get_reqqty_pk(deserialized_object, model):
    """Returns the pk of a ReqQty object with deserialized_object attributes."""
    try:
        obj = model.objects.get(
            allowance_id = deserialized_object.object.allowance.pk,
            base_id = deserialized_object.object.base.pk,
            )
        return obj.pk
    except:
        return None

def serialize_allowance(allowance):
    """Exports an allowance into the format used by the broadcaster."""
    # Molecules used by the allowance
    molecule_list = models.Molecule.objects.filter(allowances__in=[allowance,])
    molecule_data = serializers.serialize("xml", molecule_list, use_natural_keys=True)

    # Required quantities for molecules
    molecule_reqqty_list = models.MoleculeReqQty.objects.filter(allowance__in=[allowance,])
    molecule_reqqty_data = serializers.serialize("xml", molecule_reqqty_list, fields=('base','required_quantity'), use_natural_keys=True)

    # Equipment used by the allowance
    equipment_list = models.Equipment.objects.filter(allowances__in=[allowance,])
    equipment_data = serializers.serialize("xml", equipment_list, use_natural_keys=True)

    # Required quantities for equipments
    equipment_reqqty_list = models.EquipmentReqQty.objects.filter(allowance__in=[allowance,])
    equipment_reqqty_data = serializers.serialize("xml", equipment_reqqty_list, fields=('base','required_quantity'), use_natural_keys=True)
    
    # Allowance record
    allowance_data = serializers.serialize("xml", (allowance,), use_natural_keys=True)

    # Returning a list with tuples: (filename, data)
    return [
        ('molecule_obj.xml', remove_pk(molecule_data)),
        ('molecule_reqqty.xml', remove_pk(molecule_reqqty_data)),
        ('equipment_obj.xml', remove_pk(equipment_data)),
        ('equipment_reqqty.xml', remove_pk(equipment_reqqty_data)),
        ('allowance.xml', remove_pk(allowance_data)),
        ]

def create_archive(allowance):
    # Creating the response (used as a file-like object)
    response = HttpResponse(content_type="application/x-compressed-tar")
    response['Content-Disposition'] = 'attachment; filename="pharmaship_{0}.tar.gz"'.format(datetime.date.today())

    # Creating the information file
    pack_info = u"[package]\nname = {0}\nauthor = {1}\ndate = {2}".format(allowance.name, "Export Pharmaship " + __version__, datetime.datetime.utcnow().isoformat())
    
    # Creating a tar.gz archive
    with tarfile.open(fileobj=response, mode='w') as tar:
        # Processing the database
        for item in serialize_allowance(allowance):
            f = io.BytesIO(item[1])
            info = tarfile.TarInfo()
            info.name = item[0]
            info.type = tarfile.REGTYPE
            info.uid = info.gid = 0
            info.uname = info.gname = "root"
            info.mtime = time.time()
            info.size = len(f.getvalue())
            tar.addfile(info, f)
        # Adding the information file
        f = io.StringIO(pack_info)
        info = tarfile.TarInfo()
        info.name = "info"
        info.type = tarfile.REGTYPE
        info.uid = info.gid = 0
        info.uname = info.gname = "root"
        info.mtime = time.time()
        info.size = len(f.getvalue())
        tar.addfile(info, f)
    return response

def import_archive(import_file):
    """Imports an archive with allowance data inside.

    This function will get first information about the uploaded file.
    Then, it updates the trusted keys keyring.

    Following the verification of the signature, it gets information
    about the key.

    If all is OK, the signed file is opened as a tarfile.
    Infomation about the package (author, name and date) are parsed.
    
    Molecule objects with no allowance (orphan) are stored for further
    treatment.
    Molecules are updated or added (if their pk cannot be determined).
    Allowance object is updated or created by the same process.
    Required quantities are erased for the allowance and re-created.

    Finally, the new orphan molecules are affected to a special
    allowance with 0 as required quantity.

    The function returns a dictionnary with information to be displayed.
    """
    # Check the format of the file
    data = {}
    data['name'] = import_file.name
    data['size'] = import_file.size
    data['type'] = import_file.content_type
    data['data'] = ""

    # Updating the keyring
    if settings.KEYRING:
        os.environ['GNUPGHOME'] = settings.KEYRING

    gpg = gpgme.Context()

    if settings.TRUSTED_GPG:
        # Removing all keys in the keyring
        try:
            for key in gpg.keylist():
                gpg.delete(key)
        except Exception:
            pass
        # Parsing the folder to import each key in the keyring
        for item in os.listdir(settings.TRUSTED_GPG):
            try:
                with open(os.path.join(settings.TRUSTED_GPG, item), 'r') as fp:
                    gpg.import_(fp)
            except Exception:
                pass

    # Verifying the signature
    clear_tar = io.BytesIO()
    verified = gpg.verify(import_file, None, clear_tar)

    # Signature data
    if verified[0].status:
        # If it is different of 0 (GPG_ERR_NO_ERROR), abort the import process
        data['error'] = "Signature not valid. Error:", verified[0].status
        return data

    fpr = verified[0].fpr
    key_id = fpr[-8:]
    key = gpg.get_key(key_id)
    data['verified'] = u"{0} [{1}]".format(key.uids[0].uid, key_id)

    # Opening the archive and processing
    try:
        with tarfile.open(fileobj=io.BytesIO(clear_tar.getvalue()), mode="r") as tar:
            for tarinfo in tar:
                # Is it a file?
                if not tarinfo.isreg():
                    raise tarfile.ReadError

                # Is it in the MANIFEST list?
                if not tarinfo.name in MANIFEST:
                    raise tarfile.ReadError

            # Now, parsing the files in the good order
            results = {}

            # Getting information from the information file
            info = ConfigParser.ConfigParser()
            info.readfp(tar.extractfile("info"))
            data['info'] = {}
            for item in info.items("package"):
                data['info'][item[0]] = item[1]

            # Detecting objects without allowance (orphan)
            no_allowance = models.Allowance.objects.get(pk=1)
            molecule_orphan_before = models.Molecule.objects.filter(allowances=no_allowance)
            equipment_orphan_before = models.Equipment.objects.filter(allowances=no_allowance)

            # Allowance
            deserialized_allowance = serializers.deserialize("xml", tar.extractfile("allowance.xml"))
            for allowance in deserialized_allowance:
                results['allowance_name'] = allowance.object.name
                allowance_pk = get_allowance_pk(allowance)
                if allowance_pk:
                    results['allowance_new'] = False
                else:
                    allowance.save()
                    results['allowance_new'] = True
                    allowance_pk = get_allowance_pk(allowance)

                break # Only one allowance per file
            allowance = models.Allowance.objects.get(pk=allowance_pk)

            # Molecules
            added_molecule = []
            # Deserialize the file
            deserialized_list = serializers.deserialize("xml", tar.extractfile("molecule_obj.xml"))
            for molecule in deserialized_list:
                if not get_molecule_pk(molecule):
                    molecule.save()
                    pk = get_molecule_pk(molecule)
                    added_molecule.append(pk)
            results['molecule'] = added_molecule

            # Required Quantities
            deserialized_reqqty = serializers.deserialize("xml", tar.extractfile("molecule_reqqty.xml"))
            results['molecule_reqqty_added'] = 0

            # Delete all required quantities entry and create new ones
            models.MoleculeReqQty.objects.filter(allowance__in = (allowance_pk, no_allowance)).delete()
            for reqqty in deserialized_reqqty:
                reqqty.object.allowance = allowance
                reqqty.save()
                results['molecule_reqqty_added'] += 1

            # Equipments
            added_equipment = []
            # Deserialize the file
            deserialized_list = serializers.deserialize("xml", tar.extractfile("equipment_obj.xml"))
            for equipment in deserialized_list:
                if not get_equipment_pk(equipment):
                    equipment.save()
                    pk = get_equipment_pk(equipment)
                    added_equipment.append(pk)
            results['equipment'] = added_equipment

            # Required Quantities
            deserialized_reqqty = serializers.deserialize("xml", tar.extractfile("equipment_reqqty.xml"))
            results['equipment_reqqty_added'] = 0

            # Delete all required quantities entry and create new ones
            models.EquipmentReqQty.objects.filter(allowance__in = (allowance_pk, no_allowance)).delete()
            for reqqty in deserialized_reqqty:
                print reqqty
                reqqty.object.allowance = allowance
                reqqty.save()
                results['equipment_reqqty_added'] += 1

            # Listing molecules with no reqqty
            molecule_orphan_after = models.Molecule.objects.filter(allowances = None)
            equipment_orphan_after = models.Equipment.objects.filter(allowances = None)
            results['molecule_orphan'] = len(molecule_orphan_after) - len(molecule_orphan_before)
            results['equipment_orphan'] = len(equipment_orphan_after) - len(equipment_orphan_before)

            # Creating reqqty with special allowance (id=1)
            for molecule in molecule_orphan_after:
                models.MoleculeReqQty.objects.create(base=molecule, allowance=no_allowance, required_quantity=0)
            for equipment in equipment_orphan_after:
                models.EquipmentReqQty.objects.create(base=equipment, allowance=no_allowance, required_quantity=0)

        # Exporting results' values for display
        data['data'] = results

    except tarfile.ReadError as e:
        data['data'] = "Not an archive: " + str(e)

    return data
