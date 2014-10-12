# -*- coding: utf-8; -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser

FUNCTIONS = (
    (u'00', _("Captain")),
    (u'10', _("Chief Officer")),
    (u'11', _("Deck Officer")),
    (u'20', _("Chief Engineer")),
    (u'21', _("Engineer")),
    (u'99', _("Ratings")),
)
DEPARTMENTS = (
    (u'D', _("Deck")),
    (u'E', _("Engine")),
    (u'C', _("Civil")),
)


class User(AbstractUser):
    function = models.CharField(_("Function"),
                                max_length=2,
                                choices=FUNCTIONS,
                                blank=True,
                                null=True
                                )


# Models
class Vessel(models.Model):
    """Vessel information."""
    name = models.CharField(_("Name"), max_length=30)
    imo = models.IntegerField("IMO", max_length=7)
    call_sign = models.CharField(_("Call Sign"), max_length=30)
    sat_phone = models.CharField(max_length=20)
    gsm_phone = models.CharField(max_length=20)
    flag = models.CharField(_("Flag"), max_length=30)
    port_of_registry = models.CharField(_("Port of Registry"), max_length=100)
    shipowner = models.CharField(_("Shipowner"), max_length=100)
    mmsi = models.IntegerField("MMSI", max_length=9)
    fax = models.CharField(max_length=20)
    email = models.EmailField(max_length=64)

    def __unicode__(self):
        return self.name


class Rank(models.Model):
    """Rank model."""
    name = models.CharField(_("Name"), max_length=30)
    department = models.CharField(_("Department"),
                                  max_length=1,
                                  choices=DEPARTMENTS,
                                  blank=True,
                                  null=True
                                  )
    # default_group = models.ForeignKey()
