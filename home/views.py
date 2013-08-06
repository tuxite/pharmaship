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
# Filename:    home/views.py
# Description: Views for Home application. Used for contact view.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

import inventory.models
from settings.models import Vessel, Application

import datetime

def delay(delta):
    """Returns the date including a delay in days."""
    return datetime.date.today() + datetime.timedelta(days=delta)

@login_required
def index(request):
    """Default view. Displays information about upcoming events."""
    medicine = {}
    medicine['expired'] = inventory.models.Medicine.objects.filter(exp_date__lte=datetime.date.today())
    medicine['reaching_expiry'] = inventory.models.Medicine.objects.filter(exp_date__lte=delay(Application.objects.latest('id').expire_date_warning_delay)).order_by('exp_date')

    delay_date = delay(Application.objects.latest('id').expire_date_warning_delay)
    today = datetime.date.today()
    
    # Get the required quantity of a molecule and compare it to the current quantity.
    allowance_list = Vessel.objects.latest('id').allowance.all()
    # Required quantities for listed allowances
    req_qty_list = inventory.models.MedicineReqQty.objects.filter(allowance__in=allowance_list).prefetch_related('inn', 'allowance')
    # Inn list
    inn_list = inventory.models.Molecule.objects.filter(allowances__in=allowance_list).distinct().prefetch_related('tag', 'medicine_items').order_by('group', 'name')
    # Medicine list
    medicine_list = inventory.models.Medicine.objects.filter(molecule__in=inn_list, used=False).distinct().prefetch_related('location')
    # Medicine quantity transaction list
    medicineqtytransaction_list = inventory.models.MedicineQtyTransaction.objects.filter(medicine__in=medicine_list).prefetch_related('medicine')
    
    # Global dictionnary
    medicine_dict = {}
    medicine_dict['nc'] = []
    medicine_dict['expired'] = []
    medicine_dict['reaching_expiry'] = []
    medicine_dict['short_supply'] = []
    medicine_dict['ordered'] = []
    material_dict = {}
    material_dict['nc'] = []
    material_dict['expired'] = []
    material_dict['reaching_expiry'] = []
    material_dict['short_supply'] = []
    material_dict['ordered'] = []
    
    for inn in inn_list:
        # Get the total quantity of attached medicines
        medicine_qty = 0
        # Finding attached medicines (Medicine)
        for medicine in inn.medicine_items.all():
            # Do not parse the used medicines (quantity = 0)
            if medicine.used:
                continue
            # Do not add the quantity if non-conform
            if medicine.nc_inn or medicine.nc_composition:
                medicine_dict['nc'].append(medicine)
                continue
            # Do not add the quantity if expired
            if medicine.exp_date < today:
                medicine_dict['expired'].append(medicine)
                continue

            # Record the medicines reaching expiry
            if medicine.exp_date < delay_date:
                medicine_dict['reaching_expiry'].append(medicine)

            # OK, we compute the quantity
            for transaction in medicineqtytransaction_list:
                if transaction.medicine == medicine:
                    medicine_qty += transaction.value

        # Required quantity
        maximum = [0,]
        additional = 0
        for item in req_qty_list:
            if item.inn == inn:
                if item.allowance.additional == True:
                    additional += item.required_quantity
                else:
                    maximum.append(item.required_quantity)
 
        req_qty = additional + max(maximum)

        # If the req_qty > medicine_qty, we add the molecule to the list
        if req_qty > medicine_qty:
            t = {"molecule":inn, "reqqty":req_qty, "qty":medicine_qty}
            medicine_dict['short_supply'].append(t)
    
    return render_to_response('index.html', {
                'user': (request.user.last_name + " " +request.user.first_name),
                'title':_("Home"),
                'rank': request.user.profile.get_rank(),
                'medicine': medicine_dict,
                'material': material_dict,
                })

def contact(request):
    """View with CCMM contact information. Available for all users."""
    title = _("Contact the CCMM")
    if request.user.is_authenticated():
        variables = {
                'title': title,
                'user':(request.user.last_name + " " +request.user.first_name),
                'rank': request.user.profile.get_rank(),
                'css':['popup',],
                }
    else:
        variables = {'title':title}
    return render_to_response('contact.html', variables)
