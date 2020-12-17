# -*- coding: utf-8; -*-
"""Inventory application constants."""
from django.utils.translation import gettext_lazy as _


# Constants
# Transaction type values
TRANSACTION_TYPE_CHOICES = (
    (1, _('In')),
    (2, _('Used')),
    (4, _('Perished')),
    (8, _('Physical Count')),
    (9, _('Other')),
    (10, _('Sent to First Aid Kit'))
)

# Medicine "dangerosity" list values
DRUG_LIST_CHOICES = (
    (0, _('None')),
    (1, _('List I')),
    (2, _('List II')),
    (9, _('Narcotics'))
)

# Dosage form possible values
DRUG_FORM_CHOICES = (
    (1, _('Tablet')),
    (2, _('Ampoule')),
    (3, _('Capsule')),
    (5, 'Lyophilisat oral'),
    (6, 'Sachet'),
    (7, _('Suppository')),
    (8, 'Capsule'),
    (9, _('Powder')),
    (10, 'Tube pommade'),
    (11, 'Tube crème'),
    (12, 'Gel buccal'),
    (13, 'Unidose gel'),

    (40, 'Seringue pré-remplie'),

    (50, 'Solution pour perfusion'),
    (51, 'Solution injectable'),
    (52, 'Solution acqueuse'),
    (53, 'Solution moussante'),
    (54, 'Solution alcoolisée'),
    (55, 'Solution auriculaire'),
    (56, 'Solution'),
    (57, 'Solution gingivale'),

    (90, 'Bouteille'),
    (91, 'Flacon'),
    (92, 'Dispositif'),
    (93, 'Pansement adhésif cutané'),
    (94, 'Unidose'),

    (100, 'Collyre unidose'),
    (101, 'Collyre flacon'),
    (102, 'Collutoire'),
    (103, 'Pommade ophtalmique')
)

# Route of administration possible values
DRUG_ROA_CHOICES = (
    (1, _('Oral')),

    (5, _('Parenteral')),
    (6, _('Subcutaneous')),

    (10, _('Topical')),
    (11, _('Transdermal')),

    (20, _('Inhalation')),
    (21, _('Nebulization')),

    (30, _('Buccal')),
    (31, _('Sublingual')),
    (32, _('Mouthwash')),
    (33, _('Dental')),

    (40, _('Rectal')),
    (41, _('Vaginal')),

    (50, _('Ocular'))
)

# Packing choices for medicines
PACKING_CHOICES = (
    (0, 'default'),
    (10, _('box')),
    (11, _('set')),
    (20, _('pair')),
    (120, _('dozen')),
)
