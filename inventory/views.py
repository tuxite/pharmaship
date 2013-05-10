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

from models import BaseDrug, Drug, DrugQtyTransaction, DrugTransaction, DrugGroup, Dotation
from forms import DeleteForm, QtyChangeForm, AddForm, AddEquivalentForm

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
def drug(request):
    """"Drugs inventory overview."""
    return render_to_response('drug_inventory.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'title':"Registre des médicaments",
                        'rank': request.user.profile.get_rank(),
                        'inn_list': BaseDrug.objects.filter(dotations__in=Vessel.objects.latest('id').dotation.all()).distinct().order_by('group'),
                        'today': datetime.date.today(),
                        'delay': delay(Application.objects.latest('id').expire_date_warning_delay),
                        'group_list' : DrugGroup.objects.all().order_by('order'), #### TODO Filter by "links"
                        'dotation_list': Vessel.objects.latest('id').dotation.all(),
                        },
                        context_instance=RequestContext(request))

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
        form = QtyChangeForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            quantity = form.cleaned_data['quantity']
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
        form = QtyChangeForm() # An unbound form

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

        return render_to_response('drug_inventory.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'title':"Registre des médicaments",
                        'rank': request.user.profile.get_rank(),
                        'inn_list': BaseDrug.objects.filter(dotations__in=dotation_filter).distinct().order_by('group'),
                        'today': datetime.date.today(),
                        'delay': delay(Application.objects.latest('id').expire_date_warning_delay),
                        'group_list' : DrugGroup.objects.all().order_by('order'), #### TODO Filter by "links"
                        'dotation_list': Vessel.objects.latest('id').dotation.all(),
                        'filter': dotation_filter, # To know which checkbox to be checked
                        },
                        context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('drug')) # Redirect after POST

@login_required
def drug_print(request):
    """Exports the drug inventory in PDF."""
    #if request.method == 'POST':
    if True:
        # Generating a HTTP response with HTML
        rendered = render_to_response('drug_report.html', {
                        'vessel': Vessel.objects.latest('id'),
                        'title':"Registre des médicaments",
                        'rank': request.user.profile.get_rank(),
                        'inn_list': BaseDrug.objects.filter(dotations__in=Vessel.objects.latest('id').dotation.all()).distinct().order_by('group'),
                        'today': datetime.date.today(),
                        'delay': delay(Application.objects.latest('id').expire_date_warning_delay),
                        'group_list' : DrugGroup.objects.all().order_by('order'), #### TODO Filter by "links"
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
