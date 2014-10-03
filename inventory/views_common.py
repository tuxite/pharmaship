# -*- coding: utf-8; -*-
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext


import models

import datetime

def delay(delta):
    """Returns the date including a delay in days."""
    return datetime.date.today() + datetime.timedelta(days=delta)

@login_required
def index(request):
    """Default view. Displays information about upcoming events."""
    delay_date = delay(models.Settings.objects.latest('id').expire_date_warning_delay)
    today = datetime.date.today()
    
    # Get the required quantity of a molecule and compare it to the current quantity.
    allowance_list = models.Settings.objects.latest('id').allowance.all()
    
    
    return render_to_response('pharmaship/index.html', {
                'user': request.user,
                'title':_("Home"),
                'molecule': molecule_parser(allowance_list, delay_date, today),
                'equipment': equipment_parser(allowance_list, delay_date, today),
                },
                context_instance=RequestContext(request))

def contact(request):
    """View with CCMM contact information. Available for all users."""
    title = _("Contact the CCMM")
    return render_to_response('pharmaship/contact.html', {
        'user': request.user,
        'title': title,
    },
    context_instance=RequestContext(request))

# Pre-treatment functions
def molecule_parser(allowance_list, delay_date, today):
    """Parses the molecule/medicine data."""

    # Required quantities for listed allowances
    req_qty_list = models.MoleculeReqQty.objects.filter(allowance__in=allowance_list).prefetch_related('base', 'allowance')
    # Molecule list
    molecule_list = models.Molecule.objects.filter(allowances__in=allowance_list).distinct().prefetch_related('tag', 'medicine_set').order_by('group', 'name')
    # Medicine list
    #medicine_list = models.Medicine.objects.filter(parent__in=molecule_list, used=False).distinct().prefetch_related('location', 'transactions', 'parent')
    # Medicine quantity transaction list
    qty_transaction_list = models.QtyTransaction.objects.filter(content_type=ContentType.objects.get_for_model(models.Medicine))
    
    # Global dictionnary
    result = {}
    result['nc'] = []
    result['expired'] = []
    result['reaching_expiry'] = []
    result['short_supply'] = []
    result['ordered'] = []
    
    for molecule in molecule_list:
        # Get the total quantity of attached medicines
        quantity = 0
        # Finding attached materials (Material)
        for medicine in molecule.medicine_set.all():
            # Do not parse the used medicines (quantity = 0)
            if medicine.used:
                continue
            # Do not add the quantity if non-conform
            if medicine.nc_molecule or medicine.nc_composition:
                result['nc'].append(medicine)
                continue
            # Do not add the quantity if expired
            if medicine.exp_date and medicine.exp_date < today:
                result['expired'].append(medicine)
                continue

            # Record the articles reaching expiry
            if medicine.exp_date and medicine.exp_date < delay_date:
                result['reaching_expiry'].append(medicine)

            # OK, we compute the quantity
            for transaction in qty_transaction_list:
                if transaction.object_id == medicine.id:
                    quantity += transaction.value

        # Required quantity
        maximum = [0,]
        additional = 0
        for item in req_qty_list:
            if item.base == molecule:
                if item.allowance.additional == True:
                    additional += item.required_quantity
                else:
                    maximum.append(item.required_quantity)
 
        req_qty = additional + max(maximum)

        # If the req_qty > quantity, we add the equipment to the list
        if req_qty > quantity:
            t = {"molecule":molecule, "reqqty":req_qty, "qty":quantity}
            result['short_supply'].append(t)

    return result

def equipment_parser(allowance_list, delay_date, today):
    """Parses the equipment/article data."""

    # Required quantities for listed allowances
    req_qty_list = models.EquipmentReqQty.objects.filter(allowance__in=allowance_list).prefetch_related('base', 'allowance')
    # Equipment list
    equipment_list = models.Equipment.objects.filter(allowances__in=allowance_list).distinct().prefetch_related('tag', 'article_set').order_by('group', 'name')
    # Article list
    #article_list = models.Article.objects.filter(parent__in=equipment_list, used=False).distinct().prefetch_related('location', 'transactions')
    # Material quantity transaction list
    qty_transaction_list = models.QtyTransaction.objects.filter(content_type=ContentType.objects.get_for_model(models.Article))
    
    # Global dictionnary
    result = {}
    result['nc'] = []
    result['expired'] = []
    result['reaching_expiry'] = []
    result['short_supply'] = []
    result['ordered'] = []
    
    for equipment in equipment_list:
        # Get the total quantity of attached materials
        quantity = 0
        # Finding attached materials (Material)
        for article in equipment.article_set.all():
            # Do not parse the used articles (quantity = 0)
            if article.used:
                continue
            # Do not add the quantity if non-conform
            if article.nc_packaging:
                result['nc'].append(article)
                continue
            # Do not add the quantity if expired
            if article.exp_date and article.exp_date < today:
                result['expired'].append(article)
                continue

            # Record the articles reaching expiry
            if article.exp_date and article.exp_date < delay_date:
                result['reaching_expiry'].append(article)

            # OK, we compute the quantity
            for transaction in qty_transaction_list:
                if transaction.object_id == article.id:
                    quantity += transaction.value

        # Required quantity
        maximum = [0,]
        additional = 0
        for item in req_qty_list:
            if item.base == equipment:
                if item.allowance.additional == True:
                    additional += item.required_quantity
                else:
                    maximum.append(item.required_quantity)
 
        req_qty = additional + max(maximum)

        # If the req_qty > quantity, we add the equipment to the list
        if req_qty > quantity:
            t = {"equipment":equipment, "reqqty":req_qty, "qty":quantity}
            result['short_supply'].append(t)

    return result
