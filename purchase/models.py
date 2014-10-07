# -*- coding: utf-8; -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

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
    item_type = models.PositiveIntegerField()

    def __unicode__(self):
        return self.name
        
    def item_name(self):
        return _(ContentType.objects.get(pk=self.item_type).name.capitalize())
        


class Settings(models.Model):
    """Application settings."""


