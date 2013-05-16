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
# Filename:    inventory/views.py
# Description: Views for Inventory application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Sum

from models import BaseDrug, Drug, DrugQtyTransaction, DrugTransaction, DrugGroup, Dotation, DrugReqQty
from forms import DeleteForm, QtyChangeForm, AddForm, AddEquivalentForm, BaseDrugLocRemForm, InfoChangeForm

from settings.models import Vessel, Application

import datetime, os.path

#~ from xhtml2pdf import pisa
from django.shortcuts import render
from weasyprint import HTML, CSS
from django.conf.global_settings import TEMPLATE_DIRS

# Functions
def slicedict(d, s):
    return {k:v for k,v in d.iteritems() if k.startswith(s)}

def delay(delta):
    """Returns the date including a delay in days."""
    return datetime.date.today() + datetime.timedelta(days=delta)

# General views
@login_required
def index(request):
    """Redirect to drugs inventory by default."""
    return HttpResponseRedirect(reverse('drug'))

@login_required
def material(request):
    """"Material inventory overview."""
    return render_to_response('layout.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'rank': request.user.profile.get_rank(),
                        'title':"Registre du matériel médical",
                        },
                        context_instance=RequestContext(request))

# Action views
@permission_required('inventory.drug.can_delete')
def drug_delete(request, drug_id):
    """Deletes a drug attached to an INN."""
    # Selecting the drug
    drug = get_object_or_404(Drug, pk=drug_id)

    if request.method == 'POST': # If the form has been submitted
        form = DeleteForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            reason = form.cleaned_data['reason']
            # Adding a transaction
            DrugQtyTransaction.objects.create(drug=drug, transaction_type=reason, value=-drug.get_quantity())
            drug.used = True
            drug.save()

            return HttpResponseRedirect(reverse('drug')) # Redirect after POST
    else:
        form = DeleteForm() # An unbound form

    return render_to_response('drug_delete.html', {
                        'title':"Supprimer un médicament",
                        'drug':drug,
                        'form': form.as_table(),
                        },
                        context_instance=RequestContext(request))

@permission_required('inventory.drug.can_change')
def drug_change(request, drug_id):
    """Change the quantity of a drug attached to an INN."""
    # Selecting the drug
    drug = get_object_or_404(Drug, pk=drug_id)

    if request.method == 'POST': # If the form has been submitted
        form = InfoChangeForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            name = form.cleaned_data['name']
            exp_date = form.cleaned_data['exp_date']
            quantity = form.cleaned_data['quantity']
            # Modifying the name
            if name != drug.name:
                drug.name = name
            # Modifying the data
            if exp_date != drug.exp_date:
                drug.exp_date = exp_date
            # Adding a transaction
            drug_quantity = drug.get_quantity()
            if quantity != drug_quantity:
                diff = quantity - drug_quantity # Computing the difference to add a transaction
                DrugQtyTransaction.objects.create(drug=drug, transaction_type=8, value=diff) # 8: Physical Count
            if quantity == 0:
                drug.used = True
            drug.save()

            return HttpResponseRedirect(reverse('drug')) # Redirect after POST
    else:
        form = InfoChangeForm(instance=drug, initial={'quantity': drug.get_quantity()}) # An unbound form

    return render_to_response('drug_change.html', {
                        'title':"Modifier la quantité",
                        'drug':drug,
                        'form': form.as_table(),
                        },
                        context_instance=RequestContext(request))

@permission_required('inventory.drug.can_change')
def drug_out(request, drug_id):
    """Change the quantity (for medical treatment reason) of a drug attached to an INN."""
    # Selecting the drug
    drug = get_object_or_404(Drug, pk=drug_id)

    if request.method == 'POST': # If the form has been submitted
        form = QtyChangeForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            quantity = form.cleaned_data['quantity']
            # Adding a transaction
            drug_quantity = drug.get_quantity()
            DrugQtyTransaction.objects.create(drug=drug, transaction_type=2, value=-quantity) # 2: Used for a treatment
            if drug_quantity - quantity == 0:
                drug.used = True
            drug.save()

            return HttpResponseRedirect(reverse('drug')) # Redirect after POST
    else:
        form = QtyChangeForm() # An unbound form

    return render_to_response('drug_out.html', {
                        'title':"Utiliser un médicament",
                        'drug':drug,
                        'form': form.as_table(),
                        },
                        context_instance=RequestContext(request))

@permission_required('inventory.drug.can_add')
def drug_add(request, inn_id):
    """Add a drug to an INN."""
    # Selecting the inn
    inn = get_object_or_404(BaseDrug, pk=inn_id)
    default_composition = u"{1} - {0}".format(inn.composition, inn.get_dosage_form_display())

    if request.method == 'POST': # If the form has been submitted
        form = AddForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            name = form.cleaned_data['name']
            nc_composition = form.cleaned_data['nc_composition']
            quantity = form.cleaned_data['quantity']
            exp_date = form.cleaned_data['exp_date']
            # Checking the conformity
            if nc_composition == default_composition:
                nc_composition = None

            # Adding the new drug
            drug = Drug.objects.create(name = name, exp_date = exp_date, nc_composition = nc_composition)
            # Adding the link
            DrugTransaction.objects.create(drug = drug, basedrug = inn)
            # Adding the transaction
            DrugQtyTransaction.objects.create(drug=drug, transaction_type=1, value=quantity) # 1: In
            return HttpResponseRedirect(reverse('drug')) # Redirect after POST
    else:
        form = AddForm(initial={'nc_composition':default_composition}) # An unbound form

    return render_to_response('drug_add.html', {
                        'title':"Ajouter un médicament",
                        'inn':inn,
                        'form': form.as_table(),
                        },
                        context_instance=RequestContext(request))

@permission_required('inventory.drug.can_add')
def drug_equivalent(request, inn_id):
    """Add a drug with a different INN than the regulation."""
    # Selecting the inn
    inn = get_object_or_404(BaseDrug, pk=inn_id)
    default_composition = u"{1} - {0}".format(inn.composition, inn.get_dosage_form_display())

    if request.method == 'POST': # If the form has been submitted
        form = AddEquivalentForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            name = form.cleaned_data['name']
            nc_composition = form.cleaned_data['nc_composition']
            nc_inn = form.cleaned_data['nc_inn']
            quantity = form.cleaned_data['quantity']
            exp_date = form.cleaned_data['exp_date']
            # Checking the conformity
            if nc_composition == default_composition:
                nc_composition = None

            # Adding the new drug
            drug = Drug.objects.create(name = name, exp_date = exp_date, nc_composition = nc_composition, nc_inn=nc_inn)
            # Adding the link
            DrugTransaction.objects.create(drug = drug, basedrug = inn)
            # Adding the transaction
            DrugQtyTransaction.objects.create(drug=drug, transaction_type=1, value=quantity) # 1: In
            return HttpResponseRedirect(reverse('drug')) # Redirect after POST
    else:
        form = AddEquivalentForm(initial={'nc_composition':default_composition}) # An unbound form

    return render_to_response('drug_add_equivalent.html', {
                        'title':"Ajouter un médicament équivalent",
                        'inn':inn,
                        'form': form.as_table(),
                        },
                        context_instance=RequestContext(request))

@login_required
def drug_filter(request):
    """Filters the list with dotation."""
    if request.method == 'POST': # If the form has been submitted
        # Parsing the "dotation-*" keys.
        dotation_filter = []
        d = slicedict(request.POST, "dotation-")
        if (u"-1" in d.values()) or (len(d) < 1):
            # All dotations linked to the vessel's settings
            return HttpResponseRedirect(reverse('drug'))
        else:
            # Parsing all dotations id
            for dotation_id in d.values():
                dotation_filter.append(Dotation.objects.get(id=int(dotation_id)))

        values, group_list = parser(dotation_filter)

        return render_to_response('drug_inventory.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'title':"Registre des médicaments",
                        'rank': request.user.profile.get_rank(),
                        'values': values,
                        'today': datetime.date.today(),
                        'delay': delay(Application.objects.latest('id').expire_date_warning_delay),
                        'group_list' : group_list,
                        'dotation_list': Vessel.objects.latest('id').dotation.all(),
                        'filter': dotation_filter, # To know which checkbox to be checked
                        },
                        context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('drug')) # Redirect after POST

@permission_required('inventory.basedrug.can_change')
def drug_locrem(request, inn_id):
    """Change the location and remark fields of an INN."""
    # Selecting the inn
    inn = get_object_or_404(BaseDrug, pk=inn_id)

    if request.method == 'POST': # If the form has been submitted
        form = BaseDrugLocRemForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            location = form.cleaned_data['location']
            remark = form.cleaned_data['remark']
            inn.location = location
            inn.remark = remark
            inn.save()
            return HttpResponseRedirect(reverse('drug')) # Redirect after POST
    else:
        form = BaseDrugLocRemForm(instance=inn) # An unbound form

    return render_to_response('drug_locrem.html', {
                        'title':"Modifier des champs",
                        'inn':inn,
                        'form': form.as_table(),
                        },
                        context_instance=RequestContext(request))
                        
@login_required
def drug_print(request):
    """Exports the drug inventory in PDF."""
    #if request.method == 'POST':
    if True:
        # Generating a HTTP response with HTML
        dotation_list = Vessel.objects.latest('id').dotation.all()
        values, group_list = parser(dotation_list)
        
        rendered = render_to_response('drug_report.html', {
                        'vessel': Vessel.objects.latest('id'),
                        'title':"Registre des médicaments",
                        'rank': request.user.profile.get_rank(),
                        'values': values,
                        'today': datetime.date.today(),
                        'delay': delay(Application.objects.latest('id').expire_date_warning_delay),
                        'dotation_list': dotation_list,
                        },
                        context_instance=RequestContext(request))
        # Creating the response
        filename = "pharmaship_drug.pdf"
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; "{0}"'.format(filename)

        # Converting it into PDF
        HTML(string=rendered.content).write_pdf(response, stylesheets=[CSS(settings.STATIC_ROOT + '/style/report.css')])
        return response
    else:
        return HttpResponseRedirect(reverse('drug'))

########################################################################
@login_required
def drug(request):
    """"Drugs inventory overview."""
    dotation_list = Vessel.objects.latest('id').dotation.all()
    values, group_list = parser(dotation_list)

    return render_to_response('drug_inventory.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'title':"Registre des médicaments",
                        'rank': request.user.profile.get_rank(),
                        'values': values,
                        'today': datetime.date.today(),
                        'delay': delay(Application.objects.latest('id').expire_date_warning_delay),
                        'group_list' : group_list,
                        'dotation_list': dotation_list,
                        },
                        context_instance=RequestContext(request))

def parser(dotation_list):
    """Parses the database to render a list of
    groups (DrugGroup) > inn (BaseDrug) > drug (Drug).

    dotation_list: list of Dotation objects used as a filter.

    Returns the list of value and the list of groups.
    """

    # Required quantities for listed dotations
    req_qty_list = DrugReqQty.objects.filter(dotation__in=dotation_list).prefetch_related('inn', 'dotation')
    # Inn list
    inn_list = BaseDrug.objects.filter(dotations__in=dotation_list).distinct().prefetch_related('tag', 'drug_items').order_by('group')
    # Drug list
    drug_list = Drug.objects.filter(basedrug__in=inn_list, used=False).distinct()
    # Drug quantity transaction list
    drugqtytransaction_list = DrugQtyTransaction.objects.filter(drug__in=drug_list).prefetch_related('drug')
    # Group list
    group_list = DrugGroup.objects.all().order_by('order') #### TODO Filter by "links"

    # Global dictionnary
    values = []
    # Adding groups (DrugGroup)
    for group in group_list:
        # Adding name
        group_dict = {'name': group,}
        # Finding attached inn (BaseDrug)
        group_inn_list = []
        for inn in inn_list:
            # More elegant way to match id?
            if inn.group_id == group.id:
                group_inn_dict = {}
                # ID
                group_inn_dict['id'] = inn.id
                # Name
                group_inn_dict['name'] = inn.name
                # Roa, Dosage_form, Composition
                group_inn_dict['roa'] = inn.get_roa_display
                group_inn_dict['dosage_form'] = inn.get_dosage_form_display
                group_inn_dict['composition'] = inn.composition
                # Drug_list
                group_inn_dict['drug_list'] = inn.get_drug_list_display
                # Location & Remark
                group_inn_dict['location'] = inn.location
                group_inn_dict['remark'] = inn.remark
                # Tags
                group_inn_dict['tag'] = inn.tag
                # Quantity
                group_inn_dict['quantity'] = 0

                group_inn_dict['drug_items'] = []
                # Finding attached drugs (Drug)
                for drug in inn.drug_items.all().order_by('exp_date'):
                    # Do not parse the used drugs (quantity = 0)
                    if drug.used == True:
                        continue
                    group_inn_drug_dict = {}
                    # ID
                    group_inn_drug_dict['id'] = drug.id
                    # Name
                    group_inn_drug_dict['name'] = drug.name
                    # Non conformity fields
                    group_inn_drug_dict['nc_composition'] = drug.nc_composition
                    group_inn_drug_dict['nc_inn'] = drug.nc_inn
                    # Expiration data
                    group_inn_drug_dict['exp_date'] = drug.exp_date
                    # Quantity
                    group_inn_drug_dict['quantity'] = 0
                    for transaction in drugqtytransaction_list:
                        if transaction.drug == drug:
                            group_inn_drug_dict['quantity'] += transaction.value
                    # Adding the drug quantity to the inn quantity
                    group_inn_dict['quantity'] += group_inn_drug_dict['quantity']
                    # Adding the drug dict to the list
                    group_inn_dict['drug_items'].append(group_inn_drug_dict)

                # Required quantity
                maximum = [0,]
                additional = 0
                for item in req_qty_list:
                    if item.inn == inn:
                        if item.dotation.additional == True:
                            additional += item.required_quantity
                        else:
                            maximum.append(item.required_quantity)
                group_inn_dict['required_quantity'] = additional + max(maximum)
                # Adding the inn dict to the list
                group_inn_list.append(group_inn_dict)
        group_dict['child'] = group_inn_list
        values.append(group_dict)

    return values, group_list


