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
# Filename:    inventory/views_equipment.py
# Description: Views for Inventory application (equipment related).
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
from django.contrib.contenttypes.models import ContentType

import models
import forms
import utils
from settings.models import Vessel

import json
import datetime

from weasyprint import HTML, CSS

# General views
@login_required
def index(request):
    """
    Medical Article inventory overview. This lists all related :model:`inventory.Equipment`
    with their associated :model:`inventory.Article`.

    **Context**

    ``RequestContext``

    ``user``
    The logged :model:`request.user`.

    ``title``
    The title of the page.

    ``Rank``
    The rank of the logged user.

    **Template**

    :template:`inventory/article_inventory.html`

    """
    allowance_list = models.Settings.objects.latest('id').allowance.all()
    location_list = models.Location.objects.all().order_by('primary', 'secondary')
    values, group_list = parser(allowance_list, location_list)

    return render_to_response('pharmaship/equipment_inventory.html', {
                        'user': request.user,
                        'title': _("Medical Article Inventory"),
                        'values': values,
                        'today': datetime.date.today(),
                        'delay': utils.delay(models.Settings.objects.latest('id').expire_date_warning_delay),
                        'group_list' : group_list,
                        'allowance_list': allowance_list,
                        'location_list': location_list,
                        'print': reverse('pharmaship_equ_print'),
                        },
                        context_instance=RequestContext(request))

@login_required
def filter(request):
    """Filters the list with allowance."""
    if request.method == 'POST': # If the form has been submitted
        # Parsing the "allowance-*" keys.
        allowance_filter = []
        d = utilsslicedict(request.POST, "allowance-")
        if (u"-1" in d.values()) or (len(d) < 1):
            # All allowances linked to the vessel's settings
            return HttpResponseRedirect(reverse('equipment'))
        else:
            # Parsing all allowances id
            for allowance_id in d.values():
                allowance_filter.append(models.Allowance.objects.get(id=int(allowance_id)))

        location_list = models.Location.objects.all().order_by('primary', 'secondary')
        values, group_list = parser(allowance_filter, location_list)

        return render_to_response('pharmaship/equipment_inventory.html', {
                        'user': request.user,
                        'title': _("Medical Article Inventory"),
                        'values': values,
                        'today': datetime.date.today(),
                        'delay': utils.delay(models.Settings.objects.latest('id').expire_date_warning_delay),
                        'group_list' : group_list,
                        'allowance_list': models.Settings.objects.latest('id').allowance.all(),
                        'location_list': location_list,
                        'filter': allowance_filter, # To know which checkbox to be checked
                        },
                        context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('equipment')) # Redirect after POST

# Action views
@permission_required('inventory.article.can_add')
def add(request, equipment_id):
    """Add a article to an equipment."""
    # Selecting the equipment
    equipment = get_object_or_404(models.Equipment, pk=equipment_id)

    if request.method == "POST" and request.is_ajax():
        form = forms.AddArticleForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            nc_packaging = form.cleaned_data['nc_packaging']
            quantity = form.cleaned_data['quantity']
            # Checking the conformity
            if nc_packaging == equipment.packaging:
                nc_packaging = None

            # Adding the new article
            article = models.Article.objects.create(
                name = form.cleaned_data['name'],
                exp_date = form.cleaned_data['exp_date'],
                nc_packaging = nc_packaging,
                location=form.cleaned_data['location'],
                parent=equipment
                )
            # Adding the transaction
            models.QtyTransaction.objects.create(content_object=article, transaction_type=1, value=quantity) # 1: In
            data = json.dumps({'success':_('Data updated'), 'id': equipment_id, 'content': update_article(equipment_id)})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
            data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
            return HttpResponseBadRequest(data, content_type = "application/json")            
    else:
        form = forms.AddArticleForm(instance=models.Article(), initial={'nc_packaging':equipment.packaging})

    # Generating the form in HTML for Bootstrap layout
    return render_to_response('html/modal.html', {
                        'title': _("Add an article"),
                        'form': form,
                        'action': _("Add this article"),
                        'close': _("Do not add"),
                        'url': reverse('pharmaship_equ_add', args=(equipment_id,)),
                        'text': u"""
                            <p>{0}</p>
                            <h3  class="text-info">{1}</h3>
                            """.format(
                                _("You are going to add an article for this equipment:"),
                                equipment.name,
                                ),
                        'foot_text': '',
                        'callback': 'updateArticle',
                        },
                        context_instance=RequestContext(request))

@permission_required('inventory.article.can_delete')
def delete(request, article_id):
    """Deletes a article attached to an equipment."""
    # Selecting the article
    article = get_object_or_404(models.Article, pk=article_id)

    if request.method == "POST" and request.is_ajax():
        form = forms.DeleteForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            reason = form.cleaned_data['reason']
            # Adding a transaction
            models.QtyTransaction.objects.create(content_object=article, transaction_type=reason, value=-article.get_quantity())
            article.used = True
            article.save()
            data = json.dumps({'success':_('Data updated'), 'id': article.parent.pk, 'content': update_article(article.parent.pk)})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
            data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
            return HttpResponseBadRequest(data, content_type = "application/json")    
    else:
        form = forms.DeleteForm()

    # Generating the form in HTML for Bootstrap layout
    return render_to_response('html/modal.html', {
                        'title': _("Delete an article"),
                        'form': form,
                        'action': _("Delete this article"),
                        'close': _("Do not delete"),
                        'url': reverse('pharmaship_equ_delete', args=(article_id,)),
                        'text': u"""
                            <p>{0}</p>
                            <h3  class="text-info">{1}</h3>
                            <p>{2} {3} ({4} {5}).</p>
                            """.format(
                                _("You are going to delete this article:"),
                                article.name,
                                _("expiring"),
                                article.exp_date,
                                _("quantity in stock:"),
                                article.get_quantity(),
                                ),
                        'foot_text': '',
                        'callback': 'updateArticle',
                        },
                        context_instance=RequestContext(request))    


@permission_required('inventory.article.can_change')
def change(request, article_id):
    """Change the quantity of a article attached to a reference article."""
    # Selecting the article
    article = get_object_or_404(models.Article, pk=article_id)

    if request.method == "POST" and request.is_ajax():
        form = forms.ChangeArticleForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            article.name = form.cleaned_data['name']
            article.exp_date = form.cleaned_data['exp_date']
            article.location = form.cleaned_data['location']
            quantity = form.cleaned_data['quantity']

            # Adding a transaction
            article_quantity = article.get_quantity()
            if quantity != article_quantity:
                diff = quantity - article_quantity # Computing the difference to add a transaction
                models.QtyTransaction.objects.create(content_object=article, transaction_type=8, value=diff) # 8: Physical Count
            if quantity == 0:
                article.used = True

            # Updating
            article.save()
            data = json.dumps({'success':_('Data updated'), 'id': article.parent.pk, 'content': update_article(article.parent.pk)})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
            data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
            return HttpResponseBadRequest(data, content_type = "application/json")    
    else:
        form = forms.ChangeArticleForm(instance=article, initial={'quantity': article.get_quantity()})

    # Generating the form in HTML for Bootstrap layout
    return render_to_response('html/modal.html', {
                        'title': _("Update an article"),
                        'form': form,
                        'action': _("Update this article"),
                        'close': _("Do not modify"),
                        'url': reverse('pharmaship_equ_change', args=(article_id,)),
                        'text': u"""
                            <p>{0}</p>
                            <h3  class="text-info">{1}</h3>
                            <p>{2} {3} ({4} {5}).</p>
                            """.format(
                                _("You are going to modify this article:"),
                                article.name,
                                _("expiring"),
                                article.exp_date,
                                _("quantity in stock:"),
                                article.get_quantity(),
                                ),
                        'foot_text': '',
                        'callback': 'updateArticle',
                        },
                        context_instance=RequestContext(request))

@permission_required('inventory.article.can_change')
def out(request, article_id):
    """Change the quantity (for medical treatment reason) of an article attached to an equipment."""
    # Selecting the article
    article = get_object_or_404(models.Article, pk=article_id)

    if request.method == "POST" and request.is_ajax():
        form = forms.QtyChangeForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            quantity = form.cleaned_data['quantity']
            # Adding a transaction
            article_quantity = article.get_quantity()
            models.QtyTransaction.objects.create(content_object=article, transaction_type=2, value=-quantity) # 2: Used for a treatment
            if article_quantity - quantity == 0:
                article.used = True
            article.save()
            data = json.dumps({'success':_('Data updated'), 'id': article.parent.pk, 'content': update_article(article.parent.pk)})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
            data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
            return HttpResponseBadRequest(data, content_type = "application/json")    
    else:
        form = forms.QtyChangeForm()

    # Generating the form in HTML for Bootstrap layout
    return render_to_response('html/modal.html', {
                        'title': _("Use an article"),
                        'form': form,
                        'action': _("Use this article"),
                        'close': _("Do not use"),
                        'url': reverse('pharmaship_equ_out', args=(article_id,)),
                        'text': u"""
                            <p>{0}</p>
                            <h3  class="text-info">{1}</h3>
                            <p>{2} {3} ({4} {5}).</p>
                            """.format(
                                _("You are going to use this article for a treatment:"),
                                article.name,
                                _("expiring"),
                                article.exp_date,
                                _("quantity in stock:"),
                                article.get_quantity(),
                                ),
                        'foot_text': '',
                        'callback': 'updateArticle',
                        },
                        context_instance=RequestContext(request))
                        
@permission_required('inventory.remark.can_change')
def remark(request, equipment_id):
    """Change the remark field of an equipment."""
    # Selecting the equipment
    equipment = get_object_or_404(models.Equipment, pk=equipment_id)
    # Selecting the remark
    try:
        remark = equipment.remark.latest('id')
    except:
        remark = models.Remark(content_object=equipment)

    if request.method == "POST" and request.is_ajax():
        form = forms.RemarkForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            text = form.cleaned_data['text']
            remark.text = text
            remark.save()
            data = json.dumps({'success':_('Data updated'), 'id': equipment_id, 'content': remark.text})
            return HttpResponse(data, content_type="application/json")
        else:
            errors = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
            data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
            return HttpResponseBadRequest(data, content_type = "application/json")    
    else:
        form = forms.RemarkForm(initial={'text':remark.text})

    # Generating the form in HTML for Bootstrap layout
    return render_to_response('html/modal.html', {
                        'title': _("Modify the remarks"),
                        'form': form,
                        'action': _("Update these remarks"),
                        'close': _("Do not modify"),
                        'url': reverse('pharmaship_equ_remark', args=(equipment_id,)),
                        'text': u"""
                            <p>{0}</p>
                            <h3  class="text-info">{1}</h3>
                            """.format(
                                _("You are going to modify the remarks of this equipment:"),
                                equipment.name,
                                ),
                        'foot_text': '',
                        'callback': 'updateRemark',
                        },
                        context_instance=RequestContext(request))

def update_article(equipment_id):
    """Renders an Equipment article to be included in the inventory view after form submission."""
    # Equipment
    equipment = get_object_or_404(models.Equipment, pk=equipment_id)
    # Calling the DB for different necessary lists
    qty_transaction_list = models.QtyTransaction.objects.filter(content_type=ContentType.objects.get_for_model(models.Article))
    remark_list = models.Remark.objects.filter(content_type=ContentType.objects.get_for_model(models.Equipment), object_id=equipment_id)
    location_list = models.Location.objects.all().order_by('primary', 'secondary')
    allowance_list = models.Settings.objects.latest('id').allowance.all()
    req_qty_list = models.EquipmentReqQty.objects.filter(allowance__in=allowance_list, base=equipment).prefetch_related('base', 'allowance')
    # Parsing the equipment
    result = parser_element(equipment, remark_list, qty_transaction_list, location_list)
    result['required_quantity'] = utils.req_qty_element(equipment, req_qty_list)

    return render_to_response('pharmaship/article_single.inc.html', {
                    'object': result,
                    }).content
                     
@login_required
def pdf_print(request):
    """Exports the article inventory in PDF."""
    # Generating a HTTP response with HTML
    allowance_list = models.Settings.objects.latest('id').allowance.all()
    location_list = models.Location.objects.all().order_by('primary', 'secondary')
    values, group_list = parser(allowance_list, location_list)

    rendered = render_to_response('pharmaship/equipment_report.html', {
                    'vessel': Vessel.objects.latest('id'),
                    'title': _("Medicine Inventory"),
                    'user': request.user,
                    'values': values,
                    'today': datetime.date.today(),
                    'delay': utils.delay(models.Settings.objects.latest('id').expire_date_warning_delay),
                    'allowance_list': allowance_list,
                    },
                    context_instance=RequestContext(request))
    # Creating the response
    filename = "pharmaship_equipment_{0}.pdf".format(datetime.date.today())
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)

    # Converting it into PDF
    HTML(string=rendered.content).write_pdf(response, stylesheets=[CSS(settings.BASE_DIR + '/inventory/static/pharmaship/css/report.css')])
    return response

# Pre-treatment function
def parser(allowance_list, location_list):
    """Parses the database to render a list of
    groups (ArticleGroup) > Equipment > Article.

    allowance_list: list of allowance objects used as a filter.
    location_list: list of Location objects.

    Returns the list of value and the list of groups.
    """

    # Required quantities for listed allowances
    req_qty_list = models.EquipmentReqQty.objects.filter(allowance__in=allowance_list).prefetch_related('base', 'allowance')
    # Equipment list
    equipment_list = models.Equipment.objects.filter(allowances__in=allowance_list).distinct().prefetch_related('tag', 'article_set', 'remark').order_by('group', 'name')
    # Article list
    #article_list = models.Article.objects.filter(parent__in=equipment_list, used=False).distinct().prefetch_related('location')
    # Article quantity transaction list
    qty_transaction_list = models.QtyTransaction.objects.filter(content_type=ContentType.objects.get_for_model(models.Article))
    # Group list
    group_list = models.EquipmentGroup.objects.all().order_by('order')
    # Remarks
    remark_list = models.Remark.objects.filter(content_type=ContentType.objects.get_for_model(models.Equipment))

    today = datetime.date.today()
    # Global dictionnary
    values = []
    # Adding groups (ArticleGroup)
    for group in group_list:
        # Adding name
        group_dict = {'name': group,}
        # Finding attached reference article
        element_list = []
        for equipment in equipment_list:
            # More elegant way to match id?
            if equipment.group_id == group.id:
                # Equipment parsing
                element_dict = parser_element(equipment, remark_list, qty_transaction_list, location_list, today)
                # Required quantity
                element_dict['required_quantity'] = utils.req_qty_element(equipment, req_qty_list)
                # Adding the equipment dict to the list
                element_list.append(element_dict)
        group_dict['child'] = element_list
        values.append(group_dict)

    return values, group_list

def parser_element(equipment, remark_list, qty_transaction_list, location_list, today=datetime.date.today()):
    """Parses the database to render a list of
    Equipment > Article.

    equipment: an Equipment object

    Returns the formatted information with articles.
    """
    element_dict = {}
    # ID
    element_dict['id'] = equipment.id
    # Name
    element_dict['name'] = equipment.name
    # Packaging, Consumable, Perishable
    element_dict['packaging'] = equipment.packaging
    element_dict['consumable'] = equipment.consumable
    element_dict['perishable'] = equipment.perishable
    # Remark
    for remark in remark_list:
        if remark in equipment.remark.all():
            element_dict['remark'] = remark
    # Tags
    element_dict['tag'] = equipment.tag
    # Picture
    if not equipment.picture:
        equipment.picture = None
    element_dict['picture'] = equipment.picture    
    # Quantity
    element_dict['quantity'] = 0

    element_dict['article_items'] = []
    # Finding attached articles (Article)
    for article in equipment.article_set.all():
        # Do not parse the used medicines (quantity = 0)
        if article.used:
            continue
        item_dict = {}
        # ID
        item_dict['id'] = article.id
        # Name
        item_dict['name'] = article.name
        # Non conformity fields
        item_dict['nc_packaging'] = article.nc_packaging
        # Expiration date
        item_dict['exp_date'] = article.exp_date
        # Location
        for location in location_list:
            if article.location_id == location.id:
                item_dict['location'] = location
        # Quantity
        item_dict['quantity'] = 0
        for transaction in qty_transaction_list:
            if transaction.object_id == article.id:
                item_dict['quantity'] += transaction.value
        # Adding the article quantity to the equipment quantity
        if not article.nc_packaging and (not article.exp_date or article.exp_date >= today):
            element_dict['quantity'] += item_dict['quantity']
        # Adding the article dict to the list
        element_dict['article_items'].append(item_dict)

    # Returning the result dictionnary
    return element_dict


