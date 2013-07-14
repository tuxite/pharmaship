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

from django.core import serializers
from django.core.files.base import ContentFile
from django.http import HttpResponse

import inventory.models
import forms

MANIFEST = [
    'molecules.xml',
    'reqqty.xml',
    'allowance.xml',
    #~ 'metadata',
    ]

def remove_pk(xml_string):
    """Removes the PK attributes to the serialized objects."""
    dom = xml.dom.minidom.parseString(xml_string)
    for node in dom.getElementsByTagName('object'):
        if node.hasAttribute("pk"):
            node.removeAttribute("pk")
    return dom.toxml("utf-8")

def get_molecule_pk(deserialized_object):
    """Returns the pk of a Molecule object with deserialized_object attributes."""
    # Unique: (name, roa, dosage_form, composition)
    try:
        obj = inventory.models.Molecule.objects.get(
            name = deserialized_object.object.name,
            roa = deserialized_object.object.roa,
            dosage_form = deserialized_object.object.dosage_form,
            composition = deserialized_object.object.composition,
            )
        return obj.pk
    except:
        return None

def get_allowance_pk(deserialized_object):
    """Returns the pk of an Allowance object with deserialized_object attributes."""
    obj = inventory.models.Allowance.objects.get(
        name = deserialized_object.object.name,
        )
    return obj.pk

def get_reqqty_pk(deserialized_object):
    """Returns the pk of a ReqQty object with deserialized_object attributes."""
    try:
        obj = inventory.models.MedicineReqQty.objects.get(
            allowance_id = deserialized_object.object.allowance.pk,
            inn_id = deserialized_object.object.inn.pk,
            )
        return obj.pk
    except:
        return None

def serialiaze_allowance(allowance):
    """Exports an allowance into the format used by the broadcaster."""
    # Molecules used by the allowance
    molecule_list = inventory.models.Molecule.objects.filter(allowances__in=[allowance,])
    molecule_data = serializers.serialize("xml", molecule_list, use_natural_keys=True)

    # Required quantities
    reqqty_list = inventory.models.MedicineReqQty.objects.filter(allowance__in=[allowance,])
    reqqty_data = serializers.serialize("xml", reqqty_list, fields=('inn','required_quantity'), use_natural_keys=True)

    # Allowance record
    allowance_data = serializers.serialize("xml", (allowance,), use_natural_keys=True)

    # Returning a list with tuples: (filename, data)
    return [('molecules.xml', remove_pk(molecule_data)), ('reqqty.xml', remove_pk(reqqty_data)), ('allowance.xml', remove_pk(allowance_data))]

def create_archive(allowance):
    # Creating the response (used as a file-like object)
    response = HttpResponse(content_type="application/x-compressed-tar")
    response['Content-Disposition'] = 'attachment; filename="phamarship_{0}.tar.gz"'.format(datetime.date.today())

    # Creating a tar.gz archive
    with tarfile.open(fileobj=response, mode='w') as tar:
        for item in serialiaze_allowance(allowance):
            f = ContentFile(item[1])
            info = tarfile.TarInfo()
            info.name = item[0]
            info.type = tarfile.REGTYPE
            info.size = len(f)
            info.uid = info.gid = 0
            info.uname = info.gname = "root"
            info.mtime = time.time()
            tar.addfile(info, f)

    return response

# Dirty
def import_archive(import_file):
    """Imports an archive with allowance data inside. Do some integrity/authencity checks."""
    # Check the format of the file
    data = {}
    data['name'] = import_file.name
    data['size'] = import_file.size
    data['type'] = import_file.content_type
    data['data'] = ""

    try:
        with tarfile.open(fileobj=import_file, mode="r") as tar:
            for tarinfo in tar:
                # Is it a file?
                if not tarinfo.isreg():
                    raise tarfile.ReadError

                # Is it in the MANIFEST list?
                if not tarinfo.name in MANIFEST:
                    raise tarfile.ReadError

            # Now, parsing the files in the good order
            results = {}
            # 0: Detecting molecules without allowance (orphan)
            orphan_list_before = inventory.models.Molecule.objects.filter(allowances=None)
            print orphan_list_before

            # 1: Molecules
            added_molecules = []
            # Deserialize the file
            deserialized_list = serializers.deserialize("xml", tar.extractfile("molecules.xml"))
            for molecule in deserialized_list:
                if not get_molecule_pk(molecule):
                    molecule.save()
                    pk = get_molecule_pk(molecule)
                    added_molecules.append(pk)
            # Results :
            results['molecules'] = len(added_molecules)
            results['molecules_pk'] = added_molecules

            # 2: Allowance
            deserialized_allowance = serializers.deserialize("xml", tar.extractfile("allowance.xml"))
            for allowance in deserialized_allowance:
                results['allowance_name'] = allowance.object.name
                allowance_pk = get_allowance_pk(allowance)
                if allowance_pk:
                    results['allowance_new'] = False
                else:
                    allowance.save()
                    results['allowance_new'] = True
                    allowance_pk = get_allowance_pk(molecule)
                results['allowance_pk'] = allowance_pk

                break # Only one allowance per file

            # 3: Required Quantities
            deserialized_reqqty = serializers.deserialize("xml", tar.extractfile("reqqty.xml"))
            results['reqqty_added'] = 0

            # Delete all required quantities entry
            inventory.models.MedicineReqQty.objects.filter(allowance=allowance_pk).delete()
            allowance = inventory.models.Allowance.objects.get(pk=allowance_pk)
            for reqqty in deserialized_reqqty:
                reqqty.object.allowance = allowance
                reqqty.save()
                results['reqqty_added'] += 1

            # 4: Listing molecules with no reqqty
            orphan_list_after = inventory.models.Molecule.objects.filter(allowances=None)
            results['orphan'] = len(orphan_list_after) - len(orphan_list_before)
            # Creating reqqty with special allowance (id=0)
            no_allowance = inventory.models.Allowance.objects.get(pk=0)
            for molecule in orphan_list_after:
                inventory.models.MedicineReqQty.create(inn=molecule, allowance=no_allowance, required_quantity=0)

        # Exporting results' values for display
        data['data'] = results

    except tarfile.ReadError as e:
        data['data'] = "Not an archive: " + str(e)


    return data
