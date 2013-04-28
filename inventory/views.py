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
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect

from models import BaseDrug, Drug, DrugQtyTransaction, DrugTransaction
from forms import DeleteForm, QtyChangeForm, AddForm, AddEquivalentForm

import datetime

@login_required
def index(request):
    """Redirect to drugs inventory by default."""
    return HttpResponseRedirect('/inventory/drugs')

@login_required
def drugs(request):
    """"Drugs inventory overview."""
    return render_to_response('drug_inventory.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'title':"Registre des médicaments",
                        'rank': request.user.profile.get_rank(),
                        'inn_list': BaseDrug.objects.all(), #### TODO Filter by dotation
                        'today': datetime.date.today()
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

@login_required
def drugs_delete(request, drug_id):
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

            return HttpResponseRedirect('/inventory/drugs') # Redirect after POST
    else:
        form = DeleteForm() # An unbound form

    return render_to_response('drug_delete.html', {
                        'title':"Supprimer un médicament",
                        'drug':drug,
                        'form': form,
                        },
                        context_instance=RequestContext(request))

@login_required
def drugs_change(request, drug_id):
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

            return HttpResponseRedirect('/inventory/drugs') # Redirect after POST
    else:
        form = QtyChangeForm() # An unbound form

    return render_to_response('drug_change.html', {
                        'title':"Modifier la quantité",
                        'drug':drug,
                        'form': form,
                        },
                        context_instance=RequestContext(request))

@login_required
def drugs_add(request, inn_id):
    """Add a drug to an INN."""
    # Selecting the inn
    inn = get_object_or_404(BaseDrug, pk=inn_id)
    default_composition = u"{2} - {0} {1}".format(inn.dose, inn.unit, inn.get_packaging_display())

    if request.method == 'POST': # If the form has been submitted
        form = AddForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            name = form.cleaned_data['name']
            nc_dose = form.cleaned_data['nc_dose']
            quantity = form.cleaned_data['quantity']
            exp_date = form.cleaned_data['exp_date']
            # Checking the conformity
            if nc_dose == default_composition:
                nc_dose = None

            # Adding the new drug
            drug = Drug.objects.create(name = name, exp_date = exp_date, nc_dose = nc_dose)
            # Adding the link
            DrugTransaction.objects.create(drug = drug, basedrug = inn)
            # Adding the transaction
            DrugQtyTransaction.objects.create(drug=drug, transaction_type=1, value=quantity) # 1: In
            return HttpResponseRedirect('/inventory/drugs') # Redirect after POST
    else:
        form = AddForm(initial={'nc_dose':default_composition}) # An unbound form

    return render_to_response('drug_add.html', {
                        'title':"Ajouter un médicament",
                        'inn':inn,
                        'form': form,
                        },
                        context_instance=RequestContext(request))


@login_required
def drugs_equivalent(request, inn_id):
    """Add a drug with a different INN than the regulation."""
    # Selecting the inn
    inn = get_object_or_404(BaseDrug, pk=inn_id)
    default_composition = u"{2} - {0} {1}".format(inn.dose, inn.unit, inn.get_packaging_display())

    if request.method == 'POST': # If the form has been submitted
        form = AddEquivalentForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            name = form.cleaned_data['name']
            nc_dose = form.cleaned_data['nc_dose']
            nc_inn = form.cleaned_data['nc_inn']
            quantity = form.cleaned_data['quantity']
            exp_date = form.cleaned_data['exp_date']
            # Checking the conformity
            if nc_dose == default_composition:
                nc_dose = None

            # Adding the new drug
            drug = Drug.objects.create(name = name, exp_date = exp_date, nc_dose = nc_dose, nc_inn=nc_inn)
            # Adding the link
            DrugTransaction.objects.create(drug = drug, basedrug = inn)
            # Adding the transaction
            DrugQtyTransaction.objects.create(drug=drug, transaction_type=1, value=quantity) # 1: In
            return HttpResponseRedirect('/inventory/drugs') # Redirect after POST
    else:
        form = AddEquivalentForm(initial={'nc_dose':default_composition}) # An unbound form

    return render_to_response('drug_add_equivalent.html', {
                        'title':"Ajouter un médicament équivalent",
                        'inn':inn,
                        'form': form,
                        },
                        context_instance=RequestContext(request))
#### TODO ####
# En-tête de fichiers (tous)
# Validation des formulaires et affichage lors d'erreurs
# Priority LOW: Ajax pour ne transférer/modifier que le nécessaire...
# Lors de l'ajout d'un équivalent, vérifier que l'utilisateur ne rentre pas une INN réglementaire.
# Labels
# Internationalization
# Bandeau pour filtrage des dénominations
