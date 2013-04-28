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
# Filename:    users/models.py
# Description: Models for Users application. Used for user's profile.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save

FUNCTIONS = (
        (u'00', "Captain"),
        (u'10', "Chief Officer"),
        (u'11', "Deck Officer"),
        (u'20', "Chief Engineer"),
        (u'21', "Engineer"),
        (u'99', "Ratings"),
    )

class UserProfile(models.Model):
    global FUNCTIONS
    user = models.OneToOneField(User)
    
    function = models.CharField(max_length=2, choices=FUNCTIONS)


    def __str__(self):
        return "%s's profile" % self.user

    def get_rank(self):
        for item in FUNCTIONS:
            if self.function == item[0]:
                return item[1]
        return self.function

# This part is to connect both Django user model and our User profile.
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)
    
post_save.connect(create_user_profile, sender=User)

User.profile = property(lambda u: u.get_profile() )
