# -*- coding: utf-8; -*-
"""Inventory application constants."""
from django.utils.translation import gettext_lazy as _


# Constants
# Transaction type values
TRANSACTION_TYPE_CHOICES = (
    (1, _('In')),  # positive
    (2, _('Used')),  # negative
    (4, _('Perished')),  # negative
    (8, _('Physical Count')),  # positive
    (9, _('Other')),  # negative
    (10, _('Sent to First Aid Kit'))  # negative
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
    (5, _('Oral Lyophilisate')),
    (6, _('Sachet')),
    (7, _('Suppository')),
    (8, _('Vial')),
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

    (90, _('Bottle')),
    (91, _('Flacon')),
    (92, 'Dispositif'),
    (93, 'Pansement adhésif cutané'),
    (94, _('Unidose')),

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
# ID value is important as starting >= 20 it defines the packing content.
# ie.. "pair" means 2 ==> [ID] 20/10 = 2
# "dozen" means 12 ==> [ID] 120/10 = 12
# ID values above 20 are divided by 10 and truncated (ie.: 3.9 means 3).
PACKING_CHOICES = (
    (0, 'default'),
    (10, _('box')),
    (11, _('set')),
    (20, _('pair')),
    (120, _('dozen')),
)
