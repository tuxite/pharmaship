# -*- coding: utf-8; -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser

import datetime

import utils

DEPARTMENTS = (
    (u'D', _("Deck")),
    (u'E', _("Engine")),
    (u'C', _("Civil")),
)

SEX = (
    (u'M', _("Male")),
    (u'F', _("Female")),
)

class Rank(models.Model):
    """Rank model."""
    name = models.CharField(_("Name"), max_length=30)
    priority = models.PositiveIntegerField()
    department = models.CharField(_("Department"),
                                  max_length=1,
                                  choices=DEPARTMENTS,
                                  blank=True,
                                  null=True
                                  )
    groups = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name


class User(AbstractUser):
    birth_date = models.DateField()
    birth_place = models.CharField(max_length=128)
    nationality = models.CharField(max_length=128)
    sex = models.CharField(max_length=1, choices=SEX)

    passport_number = models.CharField(max_length=10)
    passport_expiry = models.DateField()

    # For permanent seaman books, leave the date empty.
    seaman_book_number = models.CharField(max_length=50)
    seaman_book_expiry = models.DateField(blank=True, null=True)

    picture = models.ImageField(upload_to=utils.filepath, blank=True, null=True)

    company_id = models.CharField(max_length=64,blank=True, null=True)

    rank = models.ForeignKey('Rank')


class Mouvement(models.Model):
    """Model to store crew mouvements signing-on/off.

    For signing-on/off at sea, use the code 'ATSEA'.
    Position: true when signing-in, false when signing off."""
    date = models.DateField(default=datetime.date.today())
    port = models.CharField(max_length=5),
    position = models.BooleanField(default=None)
    user = models.ForeignKey('User')


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



