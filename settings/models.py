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
# Filename:    settings/models.py
# Description: Models for Settings application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
   
FUNCTIONS = (
        (u'00', "Captain"),
        (u'10', "Chief Officer"),
        (u'11', "Deck Officer"),
        (u'20', "Chief Engineer"),
        (u'21', "Engineer"),
        (u'99', "Ratings"),
    )
DEPARTMENTS = (
    (u'D', "Deck"),
    (u'E', "Engine"),
    (u'C', "Civil"),
)

class User(AbstractUser):    
    function = models.CharField(_("Function"), max_length=2, choices=FUNCTIONS, blank=True, null=True)
    
# Models
class Vessel(models.Model):
    """Vessel information."""
    name = models.CharField(_("Name"), max_length=30)
    imo = models.IntegerField("IMO", max_length=7)
    call_sign = models.CharField(_("Call Sign"), max_length=30)
    sat_phone = models.CharField(max_length=20)
    gsm_phone = models.CharField(max_length=20)
    flag = models.CharField(_("Flag"), max_length=30)
    port_of_registry = models.CharField(_("Port of Registry"), max_length=100)
    shipowner = models.CharField(_("Shipowner"), max_length=100)
    mmsi = models.IntegerField("MMSI", max_length=9)
    fax = models.CharField(max_length=20)
    email = models.EmailField(max_length=64)

    def __unicode__(self):
        return self.name

class Rank(models.Model):
    """Rank model."""
    name = models.CharField(_("Name"), max_length=30)
    department = models.CharField(_("Department"), max_length=1, choices=DEPARTMENTS, blank=True, null=True)
    #default_group = models.ForeignKey()
