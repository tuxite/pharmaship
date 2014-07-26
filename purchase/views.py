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
# Filename:    purchase/views.py
# Description: Views for Purchase application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse

from django.contrib.contenttypes.models import ContentType

import models
import forms

import json, time

@login_required
def index(request):
    """Default view. Displays an overview of the requisitions."""

    return render_to_response('purchase/index.html', {
                    'user': request.user,
                    'title': _("Requisition Overview"),
                    'requisition_list': models.Requisition.objects.all(),
                    },
                    context_instance=RequestContext(request))

@permission_required('purchase.requisition.can_change')
def requisition(request, requisition_id):
    """Shows the requisition."""
    # Selecting the requisition
    requisition = get_object_or_404(models.Requisition, pk=requisition_id)

    return render_to_response('purchase/requisition.html', {
                    'user': request.user,
                    'title': _("Requisition Details"),
                    'requisition': requisition,
                    'print': reverse('purchase_req_print', args=(requisition_id,)),
                    },
                    context_instance=RequestContext(request))

@permission_required('purchase.item.can_delete')
def item_delete(request, item_id, requisition_id):
    """Deletes an item from a requisition."""
    # Selecting the item
    item = get_object_or_404(models.Item, pk=item_id)
    item.delete()
    return HttpResponseRedirect(reverse('req_view', args=(requisition_id,)))

@permission_required('purchase.requisition.can_change')
def instructions(request, requisition_id):
    """Updates the instructions of a requisition."""
    # Selecting the requisition
    requisition = get_object_or_404(models.Requisition, pk=requisition_id)
    # Parsing the form
    if request.method == 'POST' and request.is_ajax(): 
        form = forms.InstructionForm(request.POST) 
        if form.is_valid(): 
            # Process the data in form.cleaned_data
            text = form.cleaned_data['text']
            requisition.instructions = text
            requisition.save()
            data = json.dumps({'success':_('Data updated')})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
            data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
            return HttpResponseBadRequest(data, content_type = "application/json")
    else:
        return HttpResponseNotAllowed(['POST',])

@permission_required('purchase.requisition.can_change')
def status(request, requisition_id):
    """Updates the status of a requisition."""
    # Selecting the requisition
    requisition = get_object_or_404(models.Requisition, pk=requisition_id)

    if request.method == "POST" and request.is_ajax():
        form = forms.StatusForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            status = form.cleaned_data['status']
            requisition.status = int(status)
            requisition.save()
            data = json.dumps({'success':_('Data updated'), 'id': requisition_id, 'status': requisition.get_status_display()})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
            data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
            return HttpResponseBadRequest(data, content_type = "application/json")    
    else:
        form = forms.StatusForm(instance=requisition)

    # Generating the form in HTML for Bootstrap layout
    return render_to_response('html/modal.html', {
                        'title': _("Modify the status"),
                        'form': form,
                        'action': _("Update the status"),
                        'close': _("Do not modify"),
                        'url': reverse('purchase_req_status', args=(requisition_id,)),
                        'text': u"""
                            <p>{0}</p>
                            <h3  class="text-info">{1}</h3>
                            """.format(
                                _("You are going to modify the status this requisition:"),
                                requisition.name,
                                ),
                        'foot_text': '',
                        'callback': 'updateStatus',
                        },
                        context_instance=RequestContext(request))    

@permission_required('purchase.requisition.can_change')
def item_add(request, requisition_id):
    """Adds an item to a requisition."""
    # Selecting the requisition
    requisition = get_object_or_404(models.Requisition, pk=requisition_id)
    # Parsing the form
    if request.method == 'POST': 
        form = forms.AddItemForm(request.POST) 
        if form.is_valid(): 
            # Create a new requisition item
            item = models.Item()
            item.content_type = ContentType.objects.get_for_id(requisition.item_type)
            item.object_id = form.cleaned_data['object_id']
            item.quantity = form.cleaned_data['quantity']
            item.requisition = requisition
            item.save()
            # Return item
            content = render_to_response('purchase/item.html', {
                    'item': item,
                    'requisition':requisition,
                    }).content             
            data = json.dumps({'content': content})
            return HttpResponse(data, content_type="application/json")
        else:
            data = json.dumps(dict([(k, [unicode(e) for e in v]) for k, v in form.errors.items()]))
            return HttpResponseBadRequest(data, content_type="application/json")



@permission_required('purchase.requisition.can_delete')
def delete(request, requisition_id):
    """Deletes a requisition."""
    # Selecting the requisition
    requisition = get_object_or_404(models.Requisition, pk=requisition_id)
    # Parsing the form
    if request.method == 'POST' and request.is_ajax():
        requisition.delete()
        data = json.dumps({'success':_('Data updated'), 'url': reverse('purchase')})
        return HttpResponse(data, content_type="application/json")

    # Generating the form in HTML for Bootstrap layout
    return render_to_response('html/modal.html', {
                        'title': _("Delete a requisition"),
                        'form': forms.RequistionDeleteForm(),
                        'action': _("Delete this requisition"),
                        'close': _("Do not delete"),
                        'url': reverse('purchase_req_delete', args=(requisition_id,)),
                        'text': u"""
                            <p>{0}</p>
                            <h3  class="text-info">{1}</h3>
                            """.format(
                                _("You are going to delete the requisition:"),
                                requisition.name,
                                ),
                        'foot_text': '',
                        'callback': 'redirect',
                        },
                        context_instance=RequestContext(request))    

@permission_required('purchase.requisition.can_create')
def create(request):
    """Creates a requisition."""
    # Parsing the form
    if request.method == 'POST' and request.is_ajax():
        form = forms.CreateRequisitionForm(request.POST) 
        if form.is_valid(): 
            # Create a new requisition item
            requisition = models.Requisition()
            requisition.name = form.cleaned_data['name']
            requisition.port_of_delivery = form.cleaned_data['port_of_delivery']
            requisition.requested_date = form.cleaned_data['requested_date']
            requisition.item_type = form.cleaned_data['item_type']
            requisition.reference = "temporary"
            requisition.status = 0 # By default, draft.
            requisition.save()
            # Automatic adding of the requested items
            if form.cleaned_data['auto_add'] == True:
                auto_add(requisition)
                
            requisition.reference = "{0}R-{1:0>4d}".format(time.strftime('%Y'), requisition.pk)
            requisition.save()
            data = json.dumps({'success':_('Data updated'), 'url': reverse('purchase_req_view', args=(requisition.pk,))})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
            data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
            return HttpResponseBadRequest(data, content_type = "application/json")    
    else:
        form = forms.CreateRequisitionForm()
    # Generating the form in HTML for Bootstrap layout
    return render_to_response('html/modal.html', {
                        'title': _("Create a requisition"),
                        'form': form,
                        'action': _("Create this requisition"),
                        'close': _("Do not create"),
                        'url': reverse('purchase_req_create'),
                        'text': '',
                        'foot_text': '',
                        'callback': 'redirect',
                        },
                        context_instance=RequestContext(request))
                            
def auto_add(requisition):
    """Automatically add missing items in a requisition."""
    
    # Selecting the items' model 
    model = ContentType.objects.get_for_id(requisition.item_type).model_class()
    # Filtering by quantity
    items = model.objects.missing()
    
    for item in items:
        # Create items of class Purchase.Item
        # TODO: Check for duplicates first!
        p = models.Item(content_object=item, quantity=item.missing, requisition=requisition)
        p.save()  

@permission_required('purchase.requisition.can_change')
def edit(request, requisition_id):
    """Changes the name of the requisition."""
    # Selecting the requisition
    requisition = get_object_or_404(models.Requisition, pk=requisition_id)

    if request.method == "POST" and request.is_ajax():
        form = forms.RequisitionNameForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            requisition.name = form.cleaned_data['name']
            # Updating
            requisition.save()
            data = json.dumps({'success':_('Data updated'), 'id': requisition_id, 'name': requisition.name})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
            data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
            return HttpResponseBadRequest(data, content_type = "application/json")    
    else:
        form = forms.RequisitionNameForm(instance=requisition)

    # Generating the form in HTML for Bootstrap layout
    return render_to_response('html/modal.html', {
                        'title': _("Change the name"),
                        'form': form,
                        'action': _("Change the name"),
                        'close': _("Do not modify"),
                        'url': reverse('purchase_req_edit', args=(requisition_id,)),
                        'text': u"""
                            <p>{0}</p>
                            <h3  class="text-info">{1}</h3>
                            """.format(
                                _("You are going to modify the name of the requisition:"),
                                requisition.reference,
                                ),
                        'foot_text': '',
                        'callback': 'updateName',
                        },
                        context_instance=RequestContext(request))

                        
def name_search(request, requisition_id):
    """Return name of elements than can be ordered for autocomplete function."""
    # Selecting the requisition
    requisition = get_object_or_404(models.Requisition, pk=requisition_id)
    # Parsing the form
    if request.method == 'POST': 
        form = forms.NameSearchForm(request.POST) 
        if form.is_valid(): 
            name = form.cleaned_data['name']
            # Selecting the items' model 
            model = ContentType.objects.get_for_id(requisition.item_type).model_class()
            # Filter items by name
            objects = model.objects.filter(name__startswith=name.title())
            response_data = []
            for item in objects:
                item_dict = {}
                item_dict['name'] = unicode(item)
                item_dict['id'] = item.pk
                response_data.append(item_dict)
                
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    # If the request is not done by POST
    data = json.dumps({'error':"Not available."})
    return HttpResponseBadRequest(data, content_type="application/json")                    

@permission_required('purchase.requisition.can_change')
def item_change(request, requisition_id):
    """Change the quantity of an item in a requisition."""
    # Selecting the requisition
    requisition = get_object_or_404(models.Requisition, pk=requisition_id)
    # Parsing the form
    if request.method == 'POST': 
        form = forms.AddItemForm(request.POST) 
        if form.is_valid(): 
            # Create a new requisition item
            item = models.Item()
            item.content_type = ContentType.objects.get_for_id(requisition.item_type)
            item.object_id = form.cleaned_data['object_id']
            item.quantity = form.cleaned_data['quantity']
            item.requisition = requisition
            item.save()
            # Return item
            content = render_to_response('purchase/item.html', {
                    'item': item,
                    'requisition':requisition,
                    }).content             
            data = json.dumps({'content': content})
            return HttpResponse(data, content_type="application/json")
        else:
            data = json.dumps(dict([(k, [unicode(e) for e in v]) for k, v in form.errors.items()]))
            return HttpResponseBadRequest(data, content_type="application/json")


def pdf_print(request, requisition_id):
    """Exports the requisition in PDF."""
    # Selecting the requisition
    requisition = get_object_or_404(models.Requisition, pk=requisition_id)

    rendered = render_to_response('planner/pdf.html', {
                    'vessel': Vessel.objects.latest('id'),
                    'title': _("Requisition"),
                    'user': request.user,
                    'values': values,
                    'today': datetime.date.today(),

                    },
                    context_instance=RequestContext(request))
    # Creating the response
    filename = "pharmaship_medicine_{0}.pdf".format(datetime.date.today())
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)

    # Converting it into PDF
    HTML(string=rendered.content).write_pdf(response, stylesheets=[CSS(settings.STATIC_ROOT + '/style/report.css')])
    return response
    
def test(request, requisition_id):
    # Selecting the requisition
    requisition = get_object_or_404(models.Requisition, pk=requisition_id)
    
    # Selecting the items' model 
    model = ContentType.objects.get_for_id(requisition.item_type).model_class()
    # Filtering by quantity
    items = model.objects.missing()

    return render_to_response('purchase/test.html', {
                    'items': items,
                    },
                    context_instance=RequestContext(request)) 
