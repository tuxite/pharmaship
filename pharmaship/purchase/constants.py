# -*- coding: utf-8; -*-
"""Constants for Purchase module."""
from django.utils.translation import gettext as _


STATUS_CHOICES = (
        (0, _('Draft')),
        (1, _('Pending Approval')),
        (2, _('Approved')),
        (3, _('Quoted')),
        (4, _('Ordered')),
        (5, _('Partially Received')),
        (6, _('Fully Received')),
        (99, _('Cancelled')),
    )
