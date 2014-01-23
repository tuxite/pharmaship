# -*- coding: utf-8; -*-
#
# (c) 2014 Association DSM, http://devmaretique.com
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
# Filename:    inventory/utils.py
# Description: Common functions for Inventory application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.2"

import datetime

def req_qty_element(element, req_qty_list):
    """ Returns the required quantity of an element from the allowance list and required quantities list."""
    # Required quantity
    maximum = [0,]
    additional = 0
    for item in req_qty_list:
        if item.base == element:
            if item.allowance.additional == True:
                additional += item.required_quantity
            else:
                maximum.append(item.required_quantity)
    return additional + max(maximum)
    
def delay(delta):
    """Returns the date including a delay in days."""
    return datetime.date.today() + datetime.timedelta(days=delta)
    
# Functions
def slicedict(d, s):
    return {k:v for k,v in d.iteritems() if k.startswith(s)}