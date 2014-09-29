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
# Filename:    purchase/models.py
# Description: Models for Purchase application.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
#from django.apps import apps

STATUS_CHOICES = (
        (0, 'Draft'),
        (1, 'Pending Approval'),
        (2, 'Approved'),
        (3, 'Quoted'),
        (4, 'Ordered'),
        (5, 'Partially Received'),
        (6, 'Fully Received'),
        (99, 'Cancelled'),
    )

#def get_model_choices():
#    """Function to parse all installed modules to get the subclass tuples."""
#    result = []
#    for application in apps.get_app_configs():
#        try:
#            obj = application.orderable()
#            result.append({'application' : application.name, 'orderable': obj})
#        except AttributeError, e:
#            #print "Error", application, e
#            continue
#        
#    print "MATT", result
#    
#    # Now parse with ContentType to get the model's id.
#    for application in result:
#        for element in application['orderable']:
#            element['id'] = element['object'].__dict__
#            print ContentType.objects.get_for_model(element['object'])
#    
#    print "MATT2", result
#    return result

class Item(models.Model):
    """Model of object that can be ordered.

    This links any object in the software in order to be orderable.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    requisition = models.ForeignKey("Requisition")

    quantity = models.PositiveIntegerField()
    additional = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.content_object.name

    def save(self, *args, **kwargs):
        """Retrieves additional information from the object choosen. 
        If the attribute is already set, no change.
        """
        if not self.additional:
            self.additional = self.content_object.order_info()
        super(Item, self).save(*args, **kwargs)


class Requisition(models.Model):
    """Model of Requisition."""
    name = models.CharField(max_length=100)
    reference = models.CharField(max_length=20)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    requested_date = models.DateField(blank=True, null=True)
    status = models.PositiveIntegerField(_("Status"), choices=STATUS_CHOICES)
    instructions = models.TextField(blank=True, null=True)
    port_of_delivery = models.CharField(max_length=5)
    item_type = models.PositiveIntegerField()#(choices=get_model_choices())

    def __unicode__(self):
        return self.name


class Settings(models.Model):
    """Application settings."""


