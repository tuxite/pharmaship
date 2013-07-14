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
from django import forms

from inventory.models import Allowance

# Models
class Vessel(models.Model):
    """Vessel information."""
    name = models.CharField(max_length=30)
    imo = models.IntegerField(max_length=7)
    call_sign = models.CharField(max_length=30)
    sat_phone = models.CharField(max_length=20)
    gsm_phone = models.CharField(max_length=20)
    flag = models.CharField(max_length=30)
    port_of_registry = models.CharField(max_length=100)
    shipowner = models.CharField(max_length=100)
    mmsi = models.IntegerField(max_length=9)
    fax = models.CharField(max_length=20)
    email = models.EmailField(max_length=64)
    allowance = models.ManyToManyField(Allowance)

    def __unicode__(self):
        return self.name


class Application(models.Model):
    """Application settings."""
    expire_date_warning_delay = models.PositiveIntegerField()
