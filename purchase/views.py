# -*- coding: utf-8; -*-
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

import datetime
import json
import time
from weasyprint import HTML, CSS

import models
import forms

from core.views import app_links
from settings.models import Vessel


@login_required
def index(request):
    """Default view. Displays an overview of the requisitions."""

    return render_to_response('purchase/index.html', {
        'user': request.user,
        'title': _("Requisition Overview"),
        'head_links': app_links(request.resolver_match.namespace),
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
        'head_links': app_links(request.resolver_match.namespace),
        'requisition': requisition,
        'print': reverse('purchase:requisition:print', args=(requisition_id,)),
        },
        context_instance=RequestContext(request))


@permission_required('purchase.item.can_delete')
def item_delete(request, item_id, requisition_id):
    """Deletes an item from a requisition."""
    # Selecting the item
    item = get_object_or_404(models.Item, pk=item_id)
    # Selecting the requisition
    requisition = get_object_or_404(models.Requisition, pk=requisition_id)
    if requisition.status == 0:
        item.delete()
        return HttpResponse('')
    else:
        data = json.dumps({'error': _('Requisition already sent!')})
        return HttpResponseBadRequest(data, content_type="application/json")


@permission_required('purchase.item.can_change')
def item_update(request):
    """Updates an item quantity."""
    # Parsing the form
    if request.method == 'POST' and request.is_ajax():
        form = forms.UpdateItemQty(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            requisition_id = form.cleaned_data['requisition_id']
            requisition = get_object_or_404(models.Requisition,
                                            pk=requisition_id)
            if requisition.status > 0:
                # The requisition as already been sent
                data = json.dumps({'error': _('Requisition already sent!')})
                return HttpResponseBadRequest(data,
                                              content_type="application/json")

            item_id = form.cleaned_data['item_id']
            item = get_object_or_404(models.Item, pk=item_id)
            item.quantity = form.cleaned_data['item_qty']
            item.save()
            data = json.dumps({'success': _('Data updated'), 'id': item_id})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict(
                [(k, [unicode(e) for e in v]) for k, v in form.errors.items()]
            )
            data = json.dumps({'error': _('Something went wrong!'),
                               'details': errors})
            return HttpResponseBadRequest(data,
                                          content_type="application/json")
    else:
        return HttpResponseNotAllowed(['POST'])


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
            data = json.dumps({'success': _('Data updated')})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict(
                [(k, [unicode(e) for e in v]) for k, v in form.errors.items()]
            )
            data = json.dumps({'error': _('Something went wrong!'),
                               'details': errors})
            return HttpResponseBadRequest(data,
                                          content_type="application/json")
    else:
        return HttpResponseNotAllowed(['POST'])


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
            data = json.dumps({'success': _('Data updated'),
                               'id': requisition_id,
                               'status': requisition.get_status_display(),
                               'code': requisition.status})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict(
                [(k, [unicode(e) for e in v]) for k, v in form.errors.items()]
            )
            data = json.dumps({'error': _('Something went wrong!'),
                               'details': errors})
            return HttpResponseBadRequest(data,
                                          content_type="application/json")
    else:
        form = forms.StatusForm(instance=requisition)

    # Generating the form in HTML for Bootstrap layout
    return render_to_response('html/modal.html', {
        'title': _("Modify the status"),
        'form': form,
        'action': _("Update the status"),
        'close': _("Do not modify"),
        'url': reverse('purchase:requisition:status', args=(requisition_id,)),
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
            # Check if there is an existing item
            if len(requisition.item_set.filter(object_id=form.cleaned_data['object_id'])) > 0:
                # The item already exists
                data = json.dumps({'error': _('This item is already in the requisition.')})
                return HttpResponseBadRequest(data, content_type="application/json")
                
            # Create a new requisition item
            item = models.Item()
            item.content_type = ContentType.objects.get_for_id(requisition.item_type)
            item.object_id = form.cleaned_data['object_id']
            item.quantity = form.cleaned_data['quantity']
            item.requisition = requisition
            item.save()
            # Return item
            content = render_to_response('purchase/item.inc.html', {
                'item': item,
                'requisition': requisition,
                }).content
            data = json.dumps({'success': _('Item added'), 'content': content})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict(
                [(k, [unicode(e) for e in v]) for k, v in form.errors.items()]
            )
            # Return only the first error to be displayed inline
            data = json.dumps({'error': errors[errors.keys()[0]]})
            return HttpResponseBadRequest(data,
                                          content_type="application/json")


@permission_required('purchase.requisition.can_delete')
def delete(request, requisition_id):
    """Deletes a requisition."""
    # Selecting the requisition
    requisition = get_object_or_404(models.Requisition, pk=requisition_id)
    # Parsing the form
    if request.method == 'POST' and request.is_ajax():
        if requisition.status > 0:
            # The requisition as already been sent
            data = json.dumps({'error': _('Requisition already sent!')})
            return HttpResponseBadRequest(data,
                                          content_type="application/json")
            
        requisition.delete()
        data = json.dumps({'success': _('Data updated'),
                           'url': reverse('purchase:index')})
        return HttpResponse(data, content_type="application/json")

    # Generating the form in HTML for Bootstrap layout
    return render_to_response('html/modal.html', {
        'title': _("Delete a requisition"),
        'form': forms.RequistionDeleteForm(),
        'action': _("Delete this requisition"),
        'close': _("Do not delete"),
        'url': reverse('purchase:requisition:delete', args=(requisition_id,)),
        'text': u"""
            <p>{0}</p>
            <h3  class="text-info">{1}</h3>
            """.format(
                _("You are going to delete the requisition:"),
                requisition.name,
            ),
        'foot_text': u'<h4 class=\'text-danger\'>{0}</h4>'.format(
            _('The deletion is permanent!')),
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
            requisition.status = 0  # By default, draft.
            requisition.save()
            # Automatic adding of the requested items
            if form.cleaned_data['auto_add'] == True:
                auto_add(requisition)

            requisition.reference = "{0}R-{1:0>4d}".format(time.strftime('%Y'),
                                                           requisition.pk)
            requisition.save()
            data = json.dumps({'success': _('Data updated'),
                               'url': reverse('purchase:requisition:view',
                                              args=(requisition.pk,)
                                              )
                               })
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict(
                [(k, [unicode(e) for e in v]) for k, v in form.errors.items()]
            )
            data = json.dumps({'error': _('Something went wrong!'),
                               'details': errors})
            return HttpResponseBadRequest(data,
                                          content_type="application/json")
    else:
        form = forms.CreateRequisitionForm()
    # Generating the form in HTML for Bootstrap layout
    return render_to_response('html/modal.html', {
        'title': _("Create a requisition"),
        'form': form,
        'action': _("Create this requisition"),
        'close': _("Do not create"),
        'url': reverse('purchase:requisition:create'),
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
        p = models.Item(content_object=item,
                        quantity=item.missing,
                        requisition=requisition)
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
            data = json.dumps({'success': _('Data updated'),
                               'id': requisition_id,
                               'name': requisition.name})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict(
                [(k, [unicode(e) for e in v]) for k, v in form.errors.items()]
            )
            data = json.dumps({'error': _('Something went wrong!'),
                               'details': errors})
            return HttpResponseBadRequest(data,
                                          content_type="application/json")
    else:
        form = forms.RequisitionNameForm(instance=requisition)

    # Generating the form in HTML for Bootstrap layout
    return render_to_response('html/modal.html', {
        'title': _("Change the name"),
        'form': form,
        'action': _("Change the name"),
        'close': _("Do not modify"),
        'url': reverse('purchase:requisition:edit', args=(requisition_id,)),
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
    """Return name of elements than can be ordered for autocomplete
    function.
    """
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
                item_dict['text'] = unicode(item)
                item_dict['id'] = item.pk
                response_data.append(item_dict)

            return HttpResponse(json.dumps(response_data),
                                content_type="application/json")
    # If the request is not done by POST
    data = json.dumps({'error': _("Not available.")})
    return HttpResponseBadRequest(data,
                                  content_type="application/json")


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
                'requisition': requisition,
                }).content
            data = json.dumps({'content': content})
            return HttpResponse(data, content_type="application/json")
        else:
            data = json.dumps(dict(
                [(k, [unicode(e) for e in v]) for k, v in form.errors.items()])
                )
            return HttpResponseBadRequest(data,
                                          content_type="application/json")


def pdf_print(request, requisition_id):
    """Exports the requisition in PDF."""
    # Selecting the requisition
    requisition = get_object_or_404(models.Requisition, pk=requisition_id)

    rendered = render_to_response('purchase/requisition_report.html', {
        'vessel': Vessel.objects.latest('id'),
        'title': _("Requisition"),
        'user': request.user,
        'requisition': requisition,
        'today': datetime.date.today(),
        },
        context_instance=RequestContext(request))

    # Creating the response
    filename = "pharmaship_requisition_{0}.pdf".format(requisition.reference)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)

    # Converting it into PDF
    html = HTML(string=rendered.content,
                base_url=request.build_absolute_uri()
                )
    html.write_pdf(response,
                   stylesheets=[
                       CSS(settings.BASE_DIR + '/purchase/static/css/purchase/report.css')
                       ])
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
