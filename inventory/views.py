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

from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Sum

import models
import forms

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
    """Redirect to medicines inventory by default."""
    return HttpResponseRedirect(reverse('medicine'))

@login_required
def material(request):
    """"Material inventory overview."""
    return render_to_response('layout.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'rank': request.user.profile.get_rank(),
                        'title':_("Medical material inventory"),
                        },
                        context_instance=RequestContext(request))

# Action views
@permission_required('inventory.medicine.can_delete')
def medicine_delete(request, medicine_id):
    """Deletes a medicine attached to an INN."""
    # Selecting the medicine
    medicine = get_object_or_404(models.Medicine, pk=medicine_id)

    if request.method == 'POST': # If the form has been submitted
        form = forms.DeleteForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            reason = form.cleaned_data['reason']
            # Adding a transaction
            models.MedicineQtyTransaction.objects.create(medicine=medicine, transaction_type=reason, value=-medicine.get_quantity())
            medicine.used = True
            medicine.save()

            return HttpResponseRedirect(reverse('medicine')) # Redirect after POST
    else:
        form = forms.DeleteForm() # An unbound form

    return render_to_response('medicine_delete.html', {
                        'title': _("Delete a medicine"),
                        'medicine':medicine,
                        'form': form.as_table(),
                        },
                        context_instance=RequestContext(request))

@permission_required('inventory.medicine.can_change')
def medicine_change(request, medicine_id):
    """Change the quantity of a medicine attached to an INN."""
    # Selecting the medicine
    medicine = get_object_or_404(models.Medicine, pk=medicine_id)

    if request.method == 'POST': # If the form has been submitted
        form = forms.InfoChangeForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            name = form.cleaned_data['name']
            exp_date = form.cleaned_data['exp_date']
            quantity = form.cleaned_data['quantity']
            # Modifying the name
            if name != medicine.name:
                medicine.name = name
            # Modifying the data
            if exp_date != medicine.exp_date:
                medicine.exp_date = exp_date
            # Adding a transaction
            medicine_quantity = medicine.get_quantity()
            if quantity != medicine_quantity:
                diff = quantity - medicine_quantity # Computing the difference to add a transaction
                models.MedicineQtyTransaction.objects.create(medicine=medicine, transaction_type=8, value=diff) # 8: Physical Count
            if quantity == 0:
                medicine.used = True
            medicine.save()

            return HttpResponseRedirect(reverse('medicine')) # Redirect after POST
    else:
        form = forms.InfoChangeForm(instance=medicine, initial={'quantity': medicine.get_quantity()}) # An unbound form

    return render_to_response('medicine_change.html', {
                        'title': _("Modify the quantity"),
                        'medicine':medicine,
                        'form': form.as_table(),
                        },
                        context_instance=RequestContext(request))
                        
@permission_required('inventory.medicine.can_change')
def medicine_out(request, medicine_id):
    """Change the quantity (for medical treatment reason) of a medicine attached to an INN."""
    # Selecting the medicine
    medicine = get_object_or_404(models.Medicine, pk=medicine_id)

    if request.method == 'POST': # If the form has been submitted
        form = forms.QtyChangeForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            quantity = form.cleaned_data['quantity']
            # Adding a transaction
            medicine_quantity = medicine.get_quantity()
            models.MedicineQtyTransaction.objects.create(medicine=medicine, transaction_type=2, value=-quantity) # 2: Used for a treatment
            if medicine_quantity - quantity == 0:
                medicine.used = True
            medicine.save()

            return HttpResponseRedirect(reverse('medicine')) # Redirect after POST
    else:
        form = forms.QtyChangeForm() # An unbound form

    return render_to_response('medicine_out.html', {
                        'title': _("Use a medicine"),
                        'medicine':medicine,
                        'form': form.as_table(),
                        },
                        context_instance=RequestContext(request))

@permission_required('inventory.medicine.can_add')
def medicine_add(request, inn_id):
    """Add a medicine to an INN."""
    # Selecting the inn
    inn = get_object_or_404(models.Molecule, pk=inn_id)
    default_composition = u"{1} - {0}".format(inn.composition, inn.get_dosage_form_display())

    if request.method == 'POST': # If the form has been submitted
        form = forms.AddForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            name = form.cleaned_data['name']
            nc_composition = form.cleaned_data['nc_composition']
            quantity = form.cleaned_data['quantity']
            exp_date = form.cleaned_data['exp_date']
            location = form.cleaned_data['location']
            # Checking the conformity
            if nc_composition == default_composition:
                nc_composition = None

            # Adding the new medicine
            medicine = models.Medicine.objects.create(name = name, exp_date = exp_date, nc_composition = nc_composition, location=location)
            # Adding the link
            models.MedicineTransaction.objects.create(medicine = medicine, molecule = inn)
            # Adding the transaction
            models.MedicineQtyTransaction.objects.create(medicine=medicine, transaction_type=1, value=quantity) # 1: In
            return HttpResponseRedirect(reverse('medicine')) # Redirect after POST
    else:
        form = forms.AddForm(instance=models.Medicine(), initial={'nc_composition':default_composition}) # An unbound form

    return render_to_response('medicine_add.html', {
                        'title': _("Add a medicine"),
                        'inn':inn,
                        'form': form.as_table(),
                        },
                        context_instance=RequestContext(request))

@permission_required('inventory.medicine.can_add')
def medicine_equivalent(request, inn_id):
    """Add a medicine with a different INN than the regulation."""
    # Selecting the inn
    inn = get_object_or_404(models.Molecule, pk=inn_id)
    default_composition = u"{1} - {0}".format(inn.composition, inn.get_dosage_form_display())

    if request.method == 'POST': # If the form has been submitted
        form = forms.AddEquivalentForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            name = form.cleaned_data['name']
            nc_composition = form.cleaned_data['nc_composition']
            nc_inn = form.cleaned_data['nc_inn']
            quantity = form.cleaned_data['quantity']
            exp_date = form.cleaned_data['exp_date']
            location = form.cleaned_data['location']
            # Checking the conformity
            if nc_composition == default_composition:
                nc_composition = None

            # Adding the new medicine
            medicine = models.Medicine.objects.create(name = name, exp_date = exp_date, nc_composition = nc_composition, nc_inn=nc_inn, location=location)
            # Adding the link
            models.MedicineTransaction.objects.create(medicine = medicine, molecule = inn)
            # Adding the transaction
            models.MedicineQtyTransaction.objects.create(medicine=medicine, transaction_type=1, value=quantity) # 1: In
            return HttpResponseRedirect(reverse('medicine')) # Redirect after POST
    else:
        form = forms.AddEquivalentForm(instance=models.Medicine(), initial={'nc_composition':default_composition}) # An unbound form

    return render_to_response('medicine_add_equivalent.html', {
                        'title': _("Add an equivalent medicine"),
                        'inn':inn,
                        'form': form.as_table(),
                        },
                        context_instance=RequestContext(request))

@login_required
def medicine_filter(request):
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

        return render_to_response('medicine_inventory.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'title': _("Medicine inventory"),
                        'rank': request.user.profile.get_rank(),
                        'values': values,
                        'today': datetime.date.today(),
                        'delay': delay(Application.objects.latest('id').expire_date_warning_delay),
                        'group_list' : group_list,
                        'allowance_list': Vessel.objects.latest('id').allowance.all(),
                        'location_list': location_list,
                        'filter': allowance_filter, # To know which checkbox to be checked
                        },
                        context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('medicine')) # Redirect after POST

@permission_required('inventory.remark.can_change')
def medicine_remark(request, inn_id):
    """Change the remark field of an INN."""
    # Selecting the inn
    inn = get_object_or_404(models.Molecule, pk=inn_id)
    # Selecting the remark
    try :
        remark = inn.remark
    except:
        remark = models.Remark()
        inn.remark = remark
        inn.save()

    if request.method == 'POST': # If the form has been submitted
        form = forms.RemarkForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            text = form.cleaned_data['text']
            remark.text = text
            remark.save()
            return HttpResponseRedirect(reverse('medicine')) # Redirect after POST
    else:
        form = forms.RemarkForm(instance=remark) # An unbound form

    return render_to_response('medicine_remark.html', {
                        'title': _("Modify the remarks"),
                        'inn':inn,
                        'form': form.as_table(),
                        },
                        context_instance=RequestContext(request))
                        
@login_required
def medicine_print(request):
    """Exports the medicine inventory in PDF."""
    # Generating a HTTP response with HTML
    allowance_list = Vessel.objects.latest('id').allowance.all()
    location_list = models.Location.objects.all().order_by('primary', 'secondary')
    values, group_list = parser(allowance_list, location_list)
    
    rendered = render_to_response('medicine_report.html', {
                    'vessel': Vessel.objects.latest('id'),
                    'title': _("Medicine inventory"),
                    'rank': request.user.profile.get_rank(),
                    'values': values,
                    'today': datetime.date.today(),
                    'delay': delay(Application.objects.latest('id').expire_date_warning_delay),
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


########################################################################
@login_required
def medicine(request):
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
    allowance_list = Vessel.objects.latest('id').allowance.all()
    location_list = models.Location.objects.all().order_by('primary', 'secondary')
    values, group_list = parser(allowance_list, location_list)

    return render_to_response('medicine_inventory.html', {
                        'user': (request.user.last_name + " " +request.user.first_name),
                        'title': _("Medicine Inventory"),
                        'rank': _(request.user.profile.get_rank()),
                        'values': values,
                        'today': datetime.date.today(),
                        'delay': delay(Application.objects.latest('id').expire_date_warning_delay),
                        'group_list' : group_list,
                        'allowance_list': allowance_list,
                        'location_list': location_list,
                        },
                        context_instance=RequestContext(request))

def parser(allowance_list, location_list):
    """Parses the database to render a list of
    groups (MedicineGroup) > inn (Molecule) > medicine (Medicine).

    allowance_list: list of allowance objects used as a filter.
    location_list: list of Location objects.

    Returns the list of value and the list of groups.
    """

    # Required quantities for listed allowances
    req_qty_list = models.MedicineReqQty.objects.filter(allowance__in=allowance_list).prefetch_related('inn', 'allowance')
    # Inn list
    inn_list = models.Molecule.objects.filter(allowances__in=allowance_list).distinct().prefetch_related('tag', 'medicine_items').order_by('group', 'name')
    # Medicine list
    medicine_list = models.Medicine.objects.filter(molecule__in=inn_list, used=False).distinct().prefetch_related('location')
    # Medicine quantity transaction list
    medicineqtytransaction_list = models.MedicineQtyTransaction.objects.filter(medicine__in=medicine_list).prefetch_related('medicine')
    # Group list
    group_list = models.MedicineGroup.objects.all().order_by('order') #### TODO Filter by "links"
    # Remarks
    remark_list = models.Remark.objects.filter(molecule__in=inn_list).distinct().prefetch_related('molecule')
    
    # Global dictionnary
    values = []
    # Adding groups (MedicineGroup)
    for group in group_list:
        # Adding name
        group_dict = {'name': group,}
        # Finding attached inn (Molecule)
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
                # Medicine_list
                group_inn_dict['medicine_list'] = inn.get_medicine_list_display
                # Remark
                for remark in remark_list:
                    if remark.molecule == inn:
                        group_inn_dict['remark'] = remark.text
                # Tags
                group_inn_dict['tag'] = inn.tag
                # Quantity
                group_inn_dict['quantity'] = 0

                group_inn_dict['medicine_items'] = []
                # Finding attached medicines (Medicine)
                for medicine in inn.medicine_items.all():#.order_by('exp_date'):
                    # Do not parse the used medicines (quantity = 0)
                    if medicine.used == True:
                        continue
                    group_inn_medicine_dict = {}
                    # ID
                    group_inn_medicine_dict['id'] = medicine.id
                    # Name
                    group_inn_medicine_dict['name'] = medicine.name
                    # Non conformity fields
                    group_inn_medicine_dict['nc_composition'] = medicine.nc_composition
                    group_inn_medicine_dict['nc_inn'] = medicine.nc_inn
                    # Expiration date
                    group_inn_medicine_dict['exp_date'] = medicine.exp_date
                    # Location
                    for location in location_list:
                        if medicine.location_id == location.id:
                            group_inn_medicine_dict['location'] = location
                    # Quantity
                    group_inn_medicine_dict['quantity'] = 0
                    for transaction in medicineqtytransaction_list:
                        if transaction.medicine == medicine:
                            group_inn_medicine_dict['quantity'] += transaction.value
                    # Adding the medicine quantity to the inn quantity
                    if not medicine.nc_inn:
                        group_inn_dict['quantity'] += group_inn_medicine_dict['quantity']
                    # Adding the medicine dict to the list
                    group_inn_dict['medicine_items'].append(group_inn_medicine_dict)

                # Required quantity
                maximum = [0,]
                additional = 0
                for item in req_qty_list:
                    if item.inn == inn:
                        if item.allowance.additional == True:
                            additional += item.required_quantity
                        else:
                            maximum.append(item.required_quantity)
                group_inn_dict['required_quantity'] = additional + max(maximum)
                # Adding the inn dict to the list
                group_inn_list.append(group_inn_dict)
        group_dict['child'] = group_inn_list
        values.append(group_dict)

    return values, group_list


