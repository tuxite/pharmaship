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

# Create your models here.
class AdditionalDotation(models.Model):
    """Addition dotation (not directly in the flag regulation)"""
    name = models.CharField(max_length=30) # Example: GSMU

    def __unicode__(self):
        return self.name


class Vessel(models.Model):
    DOTATIONS = (
        ('A', "Dotation A"),
        ('B', "Dotation B"),
        ('C', "Dotation C"),
        )
    SPECIAL = (
        ('NA', "Sans complément"),
        ('P1', "Complément P1"),
        ('P2', "Complément P2"),
        ('P3', "Complément P3"),
        ('P4', "Complément P4"),
    )
    name = models.CharField(max_length=30)
    imo = models.IntegerField(max_length=7)
    call_sign = models.CharField(max_length=30)
    sat_phone = models.CharField(max_length=20)
    gsm_phone = models.CharField(max_length=20)
    flag = models.CharField(max_length=30)
    shipowner = models.CharField(max_length=64)
    mmsi = models.IntegerField(max_length=9)
    fax = models.CharField(max_length=20)
    email = models.EmailField(max_length=64)
    dotation = models.CharField(max_length=1, choices=DOTATIONS)
    special = models.CharField('Complement', max_length=2, choices=SPECIAL)
    additional_dotation = models.ManyToManyField(AdditionalDotation)

    def __unicode__(self):
        return self.name
 
