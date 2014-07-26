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

from django.utils.translation import ugettext as _
from django.core import serializers
from django.http import HttpResponse
from django.conf import settings

import models
import forms

from core.import_data import remove_pk

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


class DataImport:
    """Class to import allowance inside the inventory module."""    
    def __init__(self, tar):
        self.tar = tar
        self.data = []
        self.module_name = __name__.split('.')[-2] + "/"
        
    def launch(self):
        """Launches the importation.

        Molecule objects with no allowance (orphan) are stored for further
        treatment.
        Molecules are updated or added (if their pk cannot be determined).
        Allowance object is updated or created by the same process.
        Required quantities are erased for the allowance and re-created.

        Finally, the new orphan molecules are affected to a special
        allowance with 0 as required quantity.
        """ 
        # Detecting objects without allowance (orphan)
        self.no_allowance = models.Allowance.objects.get(pk=1)
        self.molecule_orphan_before = models.Molecule.objects.filter(allowances=self.no_allowance)
        self.equipment_orphan_before = models.Equipment.objects.filter(allowances=self.no_allowance)
        
        # Allowance
        try:
            deserialized_allowance = serializers.deserialize("xml", self.tar.extractfile(self.module_name + "allowance.xml"))
        except KeyError as e:
            self.error = _("File not found.") + str(e) 
            return False
            
        for allowance in deserialized_allowance:
            self.data.append({'name': _('Allowance name'), 'value': allowance.object.name})
            allowance_pk = get_allowance_pk(allowance)
            if allowance_pk:
                self.data.append({'name': _('New Allowance'), 'value': False})
            else:
                allowance.save()
                self.data.append({'name': _('New Allowance'), 'value': True})
                allowance_pk = get_allowance_pk(allowance)

            break # TODO: Only one allowance per file?
        allowance = models.Allowance.objects.get(pk=allowance_pk)

        # Molecules
        added_molecule = []
        
        # Deserialize the file
        try:
            deserialized_list = serializers.deserialize("xml", self.tar.extractfile(self.module_name + "molecule_obj.xml"))
        except KeyError as e:
            self.error = _("File not found.") + str(e) 
            return False
             
        for molecule in deserialized_list:
            if not get_molecule_pk(molecule):
                molecule.save()
                pk = get_molecule_pk(molecule)
                added_molecule.append(pk)
        self.data.append({'name': _('Added Molecules'), 'value': added_molecule})

        # Required Quantities
        try:
            deserialized_reqqty = serializers.deserialize("xml", self.tar.extractfile(self.module_name + "molecule_reqqty.xml"))
        except KeyError as e:
            self.error = _("File not found.") + str(e) 
            return False
                        
        molecule_reqqty_added = 0

        # Delete all required quantities entry and create new ones
        models.MoleculeReqQty.objects.filter(allowance__in = (allowance_pk, self.no_allowance)).delete()
        for reqqty in deserialized_reqqty:
            reqqty.object.allowance = allowance
            reqqty.save()
            molecule_reqqty_added += 1

        self.data.append({'name': _('Molecule Required Quantities Added'), 'value': molecule_reqqty_added})
        # Equipments
        added_equipment = []
        # Deserialize the file
        try:
            deserialized_list = serializers.deserialize("xml", self.tar.extractfile(self.module_name + "equipment_obj.xml"))
        except KeyError as e:
            self.error = _("File not found.") + str(e) 
            return False
                    
        for equipment in deserialized_list:
            if not get_equipment_pk(equipment):
                equipment.save()
                pk = get_equipment_pk(equipment)
                added_equipment.append(pk)
        self.data.append({'name': _('Added Equipments'), 'value': added_equipment})

        # Required Quantities
        try:
            deserialized_reqqty = serializers.deserialize("xml", self.tar.extractfile(self.module_name + "equipment_reqqty.xml"))
        except KeyError as e:
            self.error = _("File not found.") + str(e) 
            return False
                    
        equipment_reqqty_added = 0

        # Delete all required quantities entry and create new ones
        models.EquipmentReqQty.objects.filter(allowance__in = (allowance_pk, self.no_allowance)).delete()
        for reqqty in deserialized_reqqty:
            print reqqty
            reqqty.object.allowance = allowance
            reqqty.save()
            equipment_reqqty_added += 1
        self.data.append({'name': _('Equipment Required Quantities Added'), 'value': equipment_reqqty_added})

        # Listing molecules with no reqqty
        self.molecule_orphan_after = models.Molecule.objects.filter(allowances = None)
        self.equipment_orphan_after = models.Equipment.objects.filter(allowances = None)
        self.data.append({'name': _('Molecule Orphans'), 'value': len(self.molecule_orphan_after) - len(self.molecule_orphan_before)})
        self.data.append({'name': _('Equipement Orphans'), 'value': len(self.equipment_orphan_after) - len(self.equipment_orphan_before)})

        # Creating reqqty with special allowance (id=1)
        for molecule in self.molecule_orphan_after:
            models.MoleculeReqQty.objects.create(base=molecule, allowance=no_allowance, required_quantity=0)
        for equipment in self.equipment_orphan_after:
            models.EquipmentReqQty.objects.create(base=equipment, allowance=no_allowance, required_quantity=0)

        # Exporting results' values for display
        return self.data
