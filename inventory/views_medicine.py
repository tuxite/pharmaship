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
# Filename:    inventory/views_medicine.py
# Description: Views for Inventory application (medicine related).
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.2"

from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType

import models
import forms
from settings.models import Vessel

import json
import datetime, os.path

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
    """
    Medicines inventory overview. This lists all related :model:`inventory.Molecule`
    with their associated :model:`inventory.Medicine`.

    **Context**

    ``RequestContext``

    ``user``
    The logged :model:`request.user`.

    ``title``
    The title of the page.

    ``Rank``
    The rank of the logged user.

    **Template**

    :template:`inventory/medicine_inventory.html`

    """
    allowance_list = models.Settings.objects.latest('id').allowance.all()
    location_list = models.Location.objects.all().order_by('primary', 'secondary')
    values, group_list = parser(allowance_list, location_list)

    return render_to_response('pharmaship/medicine_inventory.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'title': _("Medicine Inventory"),
                        'rank': _(request.user.profile.get_rank()),
                        'values': values,
                        'today': datetime.date.today(),
                        'delay': delay(models.Settings.objects.latest('id').expire_date_warning_delay),
                        'group_list' : group_list,
                        'allowance_list': allowance_list,
                        'location_list': location_list,
                        },
                        context_instance=RequestContext(request))

@login_required
def filter(request):
    """Filters the list with allowance."""
    if request.method == 'POST': # If the form has been submitted
        # Parsing the "allowance-*" keys.
        allowance_filter = []
        d = slicedict(request.POST, "allowance-")
        if (u"-1" in d.values()) or (len(d) < 1):
            # All allowances linked to the vessel's settings
            return HttpResponseRedirect(reverse('medicine'))
        else:
            # Parsing all allowances id
            for allowance_id in d.values():
                allowance_filter.append(models.Allowance.objects.get(id=int(allowance_id)))

        location_list = models.Location.objects.all().order_by('primary', 'secondary')
        values, group_list = parser(allowance_filter, location_list)

        return render_to_response('pharmaship/medicine_inventory.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'title': _("Medicine Inventory"),
                        'rank': request.user.profile.get_rank(),
                        'values': values,
                        'today': datetime.date.today(),
                        'delay': delay(models.Settings.objects.latest('id').expire_date_warning_delay),
                        'group_list' : group_list,
                        'allowance_list': models.Settings.objects.latest('id').allowance.all(),
                        'location_list': location_list,
                        'filter': allowance_filter, # To know which checkbox to be checked
                        },
                        context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('medicine')) # Redirect after POST

# Action views
@permission_required('inventory.medicine.can_delete')
def delete(request, medicine_id):
    """Deletes a medicine attached to a molecule."""
    # Selecting the medicine
    medicine = get_object_or_404(models.Medicine, pk=medicine_id)

    if request.method == "POST" and request.is_ajax():
        form = forms.DeleteForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            reason = form.cleaned_data['reason']
            # Adding a transaction
            models.QtyTransaction.objects.create(content_object=medicine, transaction_type=reason, value=-medicine.get_quantity())

            medicine.used = True
            medicine.save()
            data = json.dumps({'id': medicine.parent.pk, 'content': update_article(medicine.parent.pk)})
            return HttpResponse(data, content_type="application/json")
        else:
            data = json.dumps(dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()]))
            return HttpResponseBadRequest(data, content_type="application/json")
    else:
        form = forms.DeleteForm()

    # Generating JSON data for AJAX
    response_data = {
        'title': _("Delete a medicine"),
        'form': form.as_table(),
        'button_OK': _("Delete this medicine"),
        'button_KO': _("Do not delete"),
        'url': reverse('med_delete', args=(medicine_id,)),
        'text': u"""
            <p>{0}</p>
            <p><b class='sky_blue'>{1}</b> {2} {3} ({4} {5}).</p>
            """.format(
                _("You are going to delete this medicine:"),
                medicine.name,
                _("expiring"),
                medicine.exp_date,
                _("quantity in stock:"),
                medicine.get_quantity(),
                ),
        'foot_text': '',
        }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@permission_required('inventory.medicine.can_change')
def change(request, medicine_id):
    """Change the quantity of a medicine attached to an INN."""
    # Selecting the medicine
    medicine = get_object_or_404(models.Medicine, pk=medicine_id)

    if request.method == "POST" and request.is_ajax():
        form = forms.InfoChangeForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            medicine.name = form.cleaned_data['name']
            medicine.exp_date = form.cleaned_data['exp_date']
            medicine.location = form.cleaned_data['location']
            quantity = form.cleaned_data['quantity']

            # Adding a transaction
            medicine_quantity = medicine.get_quantity()
            if quantity != medicine_quantity:
                diff = quantity - medicine_quantity # Computing the difference to add a transaction
                models.QtyTransaction.objects.create(content_object=medicine, transaction_type=8, value=diff) # 8: Physical Count
            if quantity == 0:
                medicine.used = True

            # Updating
            medicine.save()
            data = json.dumps({'id': medicine.parent.pk, 'content': update_article(medicine.parent.pk)})
            return HttpResponse(data, content_type="application/json")
        else:
            data = json.dumps(dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()]))
            return HttpResponseBadRequest(data, content_type="application/json")
    else:
        form = forms.InfoChangeForm(instance=medicine, initial={'quantity': medicine.get_quantity()})

    # Generating JSON data for AJAX
    response_data = {
        'title': _("Update a medicine"),
        'form': form.as_table(),
        'button_OK': _("Update this medicine"),
        'button_KO': _("Do not modify"),
        'url': reverse('med_change', args=(medicine_id,)),
        'text': u"""
            <p>{0}</p>
            <p><b class='sky_blue'>{1}</b> {2} {3} ({4} {5}).</p>
            """.format(
                _("You are going to modify this medicine:"),
                medicine.name,
                _("expiring"),
                medicine.exp_date,
                _("quantity in stock:"),
                medicine.get_quantity(),
                ),
        'foot_text': '',
        }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@permission_required('inventory.medicine.can_change')
def out(request, medicine_id):
    """Change the quantity (for medical treatment reason) of a medicine attached to an INN."""
    # Selecting the medicine
    medicine = get_object_or_404(models.Medicine, pk=medicine_id)

    if request.method == "POST" and request.is_ajax():
        form = forms.QtyChangeForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            quantity = form.cleaned_data['quantity']
            # Adding a transaction
            medicine_quantity = medicine.get_quantity()
            models.QtyTransaction.objects.create(content_object=medicine, transaction_type=2, value=-quantity) # 2: Used for a treatment
            if medicine_quantity - quantity == 0:
                medicine.used = True
            medicine.save()
            data = json.dumps({'id': medicine.parent.pk, 'content': update_article(medicine.parent.pk)})
            return HttpResponse(data, content_type="application/json")
        else:
            data = json.dumps(dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()]))
            return HttpResponseBadRequest(data, content_type="application/json")
    else:
        form = forms.QtyChangeForm() # An unbound form

    # Generating JSON data for AJAX
    response_data = {
        'title': _("Use a medicine"),
        'form': form.as_table(),
        'button_OK': _("Use this medicine"),
        'button_KO': _("Do not use"),
        'url': reverse('med_out', args=(medicine_id,)),
        'text': u"""
            <p>{0}</p>
            <p><b class='sky_blue'>{1}</b> {2} {3} ({4} {5}).</p>
            """.format(
                _("You are going to use this medicine for a treatment:"),
                medicine.name,
                _("expiring"),
                medicine.exp_date,
                _("quantity in stock:"),
                medicine.get_quantity(),
                ),
        'foot_text': '',
        }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@permission_required('inventory.medicine.can_add')
def add(request, molecule_id):
    """Add a medicine to a molecule."""
    # Selecting the molecule
    molecule = get_object_or_404(models.Molecule, pk=molecule_id)
    default_composition = u"{1} - {0}".format(molecule.composition, molecule.get_dosage_form_display())

    if request.method == "POST" and request.is_ajax():
        form = forms.AddForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            nc_composition = form.cleaned_data['nc_composition']
            quantity = form.cleaned_data['quantity']
            # Checking the conformity
            if nc_composition == default_composition:
                nc_composition = None

            # Adding the new medicine
            medicine = models.Medicine.objects.create(
                name = form.cleaned_data['name'],
                exp_date = form.cleaned_data['exp_date'],
                location = form.cleaned_data['location'],
                nc_composition = nc_composition,
                parent = molecule,
                )
            # Adding the transaction
            models.QtyTransaction.objects.create(content_object=medicine, transaction_type=1, value=quantity) # 1: In
            data = json.dumps({'id': molecule_id, 'content': update_article(molecule_id)})
            return HttpResponse(data, content_type="application/json")
        else:
            data = json.dumps(dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()]))
            return HttpResponseBadRequest(data, content_type="application/json")
    else:
        form = forms.AddForm(instance=models.Medicine(), initial={'nc_composition':default_composition})

    # Generating JSON data for AJAX
    response_data = {
        'title': _("Add a medicine"),
        'form': form.as_table(),
        'button_OK': _("Add this medicine"),
        'button_KO': _("Do not add"),
        'url': reverse('med_add', args=(molecule_id,)),
        'text': u"""
            <p>{0}</p>
            <p><b class='sky_blue'>{1}</b></p>
            """.format(
                _("You are going to add a medicine for this molecule:"),
                molecule.name,
                ),
        'foot_text': '',
        }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@permission_required('inventory.medicine.can_add')
def equivalent(request, molecule_id):
    """Add a medicine with a different molecule than the allowance."""
    # Selecting the molecule
    molecule = get_object_or_404(models.Molecule, pk=molecule_id)
    default_composition = u"{1} - {0}".format(molecule.composition, molecule.get_dosage_form_display())

    if request.method == "POST" and request.is_ajax():
        form = forms.AddEquivalentForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            nc_composition = form.cleaned_data['nc_composition']
            quantity = form.cleaned_data['quantity']
            # Checking the conformity
            if nc_composition == default_composition:
                nc_composition = None

            # Adding the new medicine
            medicine = models.Medicine.objects.create(
                name = form.cleaned_data['name'],
                exp_date = form.cleaned_data['exp_date'],
                location = form.cleaned_data['location'],
                nc_molecule = form.cleaned_data['nc_molecule'],
                nc_composition = nc_composition,
                parent = molecule,
                )
            # Adding the transaction
            models.QtyTransaction.objects.create(content_object=medicine, transaction_type=1, value=quantity) # 1: In
            data = json.dumps({'id': molecule_id, 'content': update_article(molecule_id)})
            return HttpResponse(data, content_type="application/json")
        else:
            data = json.dumps(dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()]))
            return HttpResponseBadRequest(data, content_type="application/json")
    else:
        form = forms.AddEquivalentForm(instance=models.Medicine(), initial={'nc_composition':default_composition})

    # Generating JSON data for AJAX
    response_data = {
        'title': _("Add an equivalent medicine"),
        'form': form.as_table(),
        'button_OK': _("Add this medicine"),
        'button_KO': _("Do not add"),
        'url': reverse('med_add', args=(molecule_id,)),
        'text': u"""
            <p>{0}</p>
            <p><b class='sky_blue'>{1}</b></p>
            """.format(
                _("You are going to add an equivalent medicine for this molecule:"),
                molecule.name,
                ),
        'foot_text': _("Before adding this equivalent medicine (molecule different from the allowance), make sure you have had the approval of a doctor."),
        }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@permission_required('inventory.remark.can_change')
def remark(request, molecule_id):
    """Change the remark field of a molecule."""
    # Selecting the molecule
    molecule = get_object_or_404(models.Molecule, pk=molecule_id)
    # Selecting the remark
    try:
        remark = molecule.remark.latest('id')
    except:
        remark = models.Remark(content_object=molecule)

    if request.method == "POST" and request.is_ajax():
        form = forms.RemarkForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            text = form.cleaned_data['text']
            remark.text = text
            remark.save()
            data = json.dumps({'id': molecule_id, 'content': update_article(molecule_id)})
            return HttpResponse(data, content_type="application/json")
        else:
            data = json.dumps(dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()]))
            return HttpResponseBadRequest(data, content_type="application/json")
    else:
        form = forms.RemarkForm(initial={'text':remark.text})

    # Generating JSON data for AJAX
    response_data = {
        'title': _("Modify the remarks"),
        'form': form.as_table(),
        'button_OK': _("Update these remarks"),
        'button_KO': _("Do not modify"),
        'url': reverse('med_remark', args=(molecule_id,)),
        'text': u"""
            <p>{0}</p>
            <p><b class='sky_blue'>{1}</b></p>
            """.format(
                _("You are going to modify the remarks of this molecule:"),
                molecule.name,
                ),
        'foot_text': '',
        }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def update_article(molecule_id):
    """Renders a Molecule <article> to be included in the inventory view after form submission."""
    # Molecule
    molecule = get_object_or_404(models.Molecule, pk=molecule_id)
    # Calling the DB for different necessary lists
    qty_transaction_list = models.QtyTransaction.objects.filter(content_type=ContentType.objects.get_for_model(models.Medicine))
    remark_list = models.Remark.objects.filter(content_type=ContentType.objects.get_for_model(models.Molecule), object_id=molecule_id)
    location_list = models.Location.objects.all().order_by('primary', 'secondary')
    allowance_list = models.Settings.objects.latest('id').allowance.all()
    req_qty_list = models.MoleculeReqQty.objects.filter(allowance__in=allowance_list, base=molecule).prefetch_related('base', 'allowance')
    # Parsing the molecule
    result = parser_element(molecule, remark_list, qty_transaction_list, location_list)
    result['required_quantity'] = req_qty_element(molecule, req_qty_list)

    return render_to_response('pharmaship/medicine_article.html', {
                    'object': result,
                    }).content

@login_required
def pdf_print(request):
    """Exports the medicine inventory in PDF."""
    # Generating a HTTP response with HTML
    allowance_list = models.Settings.objects.latest('id').allowance.all()
    location_list = models.Location.objects.all().order_by('primary', 'secondary')
    values, group_list = parser(allowance_list, location_list)

    rendered = render_to_response('pharmaship/medicine_report.html', {
                    'vessel': Vessel.objects.latest('id'),
                    'title': _("Medicine Inventory"),
                    'rank': request.user.profile.get_rank(),
                    'values': values,
                    'today': datetime.date.today(),
                    'delay': delay(models.Settings.objects.latest('id').expire_date_warning_delay),
                    'allowance_list': allowance_list,
                    },
                    context_instance=RequestContext(request))
    # Creating the response
    filename = "pharmaship_medicine_{0}.pdf".format(datetime.date.today())
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)

    # Converting it into PDF
    HTML(string=rendered.content).write_pdf(response, stylesheets=[CSS(settings.STATIC_ROOT + '/style/report.css')])
    return response

# Pre-treatment function
def parser(allowance_list, location_list):
    """Parses the database to render a list of
    MoleculeGroup > Molecule > Medicine.

    allowance_list: list of allowance objects used as a filter.
    location_list: list of Location objects.

    Returns the list of value and the list of groups.
    """

    # Required quantities for listed allowances
    req_qty_list = models.MoleculeReqQty.objects.filter(allowance__in=allowance_list).prefetch_related('base', 'allowance')
    # Molecule list
    molecule_list = models.Molecule.objects.filter(allowances__in=allowance_list).distinct().prefetch_related('tag', 'medicine_set', 'remark').order_by('group', 'name')
    # Medicine list
    medicine_list = models.Medicine.objects.filter(parent__in=molecule_list, used=False).distinct().prefetch_related('location', 'transactions')
    # Medicine quantity transaction list
    qty_transaction_list = models.QtyTransaction.objects.filter(content_type=ContentType.objects.get_for_model(models.Medicine))
    # Group list
    group_list = models.MoleculeGroup.objects.all().order_by('order')
    # Remarks
    remark_list = models.Remark.objects.filter(content_type=ContentType.objects.get_for_model(models.Molecule))

    today = datetime.date.today()
    # Global dictionnary
    values = []
    # Adding groups (MedicineGroup)
    for group in group_list:
        # Adding name
        group_dict = {'name': group,}
        # Finding attached inn (Molecule)
        group_molecule_list = []
        for molecule in molecule_list:
            # More elegant way to match id?
            if molecule.group_id == group.id:
                # Molecule parsing
                group_molecule_dict = parser_element(molecule, remark_list, qty_transaction_list, location_list, today)
                # Required quantity
                group_molecule_dict['required_quantity'] = req_qty_element(molecule, req_qty_list)
                # Adding the molecule dict to the list
                group_molecule_list.append(group_molecule_dict)
        group_dict['child'] = group_molecule_list
        values.append(group_dict)

    return values, group_list

def parser_element(molecule, remark_list, qty_transaction_list, location_list, today=datetime.date.today()):
    """Parses the database to render a list of
    Molecule > Medicine.

    molecule: a Molecule object

    Returns the formatted information with medicines.
    """
    element_dict = {}
    # ID
    element_dict['id'] = molecule.id
    # Name
    element_dict['name'] = molecule.name
    # Roa, Dosage_form, Composition
    element_dict['roa'] = molecule.get_roa_display
    element_dict['dosage_form'] = molecule.get_dosage_form_display
    element_dict['composition'] = molecule.composition
    # Medicine_list
    element_dict['medicine_list'] = molecule.get_medicine_list_display
    # Remark
    for remark in remark_list:
        if remark in molecule.remark.all():
            element_dict['remark'] = remark
    # Tags
    element_dict['tag'] = molecule.tag
    # Quantity
    element_dict['quantity'] = 0

    element_dict['medicine_items'] = []
    # Finding attached medicines (Medicine)
    for medicine in molecule.medicine_set.all():
        # Do not parse the used medicines (quantity = 0)
        if medicine.used:
            continue
        item_dict = {}
        # ID
        item_dict['id'] = medicine.id
        # Name
        item_dict['name'] = medicine.name
        # Non conformity fields
        item_dict['nc_composition'] = medicine.nc_composition
        item_dict['nc_molecule'] = medicine.nc_molecule
        # Expiration date
        item_dict['exp_date'] = medicine.exp_date
        # Location
        for location in location_list:
            if medicine.location_id == location.id:
                item_dict['location'] = location
        # Quantity
        item_dict['quantity'] = 0
        for transaction in qty_transaction_list:
            if transaction.object_id == medicine.id:
                item_dict['quantity'] += transaction.value
        # Adding the medicine quantity to the molecule quantity
        if not medicine.nc_molecule and not medicine.nc_composition and medicine.exp_date >= today:
            element_dict['quantity'] += item_dict['quantity']
        # Adding the medicine dict to the list
        element_dict['medicine_items'].append(item_dict)
    # Returning the result dictionnary
    return element_dict

def req_qty_element(molecule, req_qty_list):
    """ Returns the required quantity of an element from the allowance list and required quantities list."""
    # Required quantity
    maximum = [0,]
    additional = 0
    for item in req_qty_list:
        if item.base == molecule:
            if item.allowance.additional == True:
                additional += item.required_quantity
            else:
                maximum.append(item.required_quantity)
    return additional + max(maximum)
