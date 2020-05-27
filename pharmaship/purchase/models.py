from django.utils.translation import gettext as _
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from pharmaship.purchase import constants


class Item(models.Model):
    """Model of object that can be ordered.

    This links any object in the software in order to be orderable.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    requisition = models.ForeignKey("Requisition", on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    additional = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.content_object.name

    def save(self, *args, **kwargs):
        """Retrieve additional information from the object choosen.

        If the attribute is already set, no change.
        """
        if not self.additional:
            self.additional = self.content_object.order_info()
        super(Item, self).save(*args, **kwargs)


class Requisition(models.Model):
    """Model of Requisition."""

    name = models.CharField(_("Name"), max_length=100)
    reference = models.CharField(_("Reference"), max_length=20)
    date_of_creation = models.DateTimeField(_("Date of Creation"), auto_now_add=True)
    requested_date = models.DateField(_("Requested Date"), blank=True, null=True)
    status = models.PositiveIntegerField(_("Status"), choices=constants.STATUS_CHOICES)
    instructions = models.TextField(_("Instructions"), blank=True, null=True)
    port_of_delivery = models.CharField(_("Port of Delivery"), max_length=5)
    item_type = models.PositiveIntegerField(_("Item Type"))

    def __str__(self):
        return self.name

    def item_name(self):
        ct = ContentType.objects.get(pk=self.item_type)
        return str(_(ct.app_label.capitalize())) + " > " + str(_(ct.name.capitalize()))
