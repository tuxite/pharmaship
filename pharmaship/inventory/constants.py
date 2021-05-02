# -*- coding: utf-8; -*-
"""Inventory application constants.

Constants used in inventory models
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* ``TRANSACTION_TYPE_CHOICES``: Except ``1`` (input of items) and
  ``8`` (actual count of items), all other values are negative for
  computing the stock.
* ``DRUG_LIST_CHOICES``: Corresponds to French medicine classification.
* ``DRUG_FORM_CHOICES``: All available medicine galenic forms.
* ``DRUG_ROA_CHOICES``: All medicine route of administration possibilities.
* ``PACKING_CHOICES``: Item packaging possibilities (in example, for
  counting by boxes, pairs...)

Transaction Type Choices
^^^^^^^^^^^^^^^^^^^^^^^^
These values are used for computing the current stock from the quantity
transactions.

When receiving an article (thus *adding* an item), the transaction value is
``1`` (input). The quantity is positive.
In all other (used/perished/other...) the quantity is considered as negative.

The "stock count" transaction (value ``8``) correspond to an actual counting
of the item. There is no addition/subtraction, the item quantity is considered
as reference.

Examples::

    Transaction type: 1 - Quantity: 10
    Transaction type: 2 - Quantity:  1
    Transaction type: 2 - Quantity:  3
    ==> Remaning: .................  6

With "stock count"::

    Transaction type: 1 - Quantity: 20
    Transaction type: 2 - Quantity:  4
    Transaction type: 8 - Quantity:  7
    ==> Remaning: .................  7

Packing Choices
^^^^^^^^^^^^^^^
Numbering of choice ID is specific and important as starting >= 20 it defines
the packing content.

ID values above 20 are divided by 10 and truncated (ie.: 3.9 means 3).

Examples::

                         ID    Formula    Result
  ----------------------------------------------
  "pair" means 2         20      20/10 =>      2
  "set of two" means 2   21      21/10 =>      2
  "dozen" means 12      120     120/10 =>     12
"""
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
    (10, _('Ointment tube')),
    (11, _('Cream tube')),
    (12, _('Oral gel')),
    (13, _('Unidose gel')),

    (40, _('Pre-filled syringe')),

    (50, _('Solution for infusion')),
    (51, _('Solution for injection')),
    (52, _('Aqueous solution')),
    (53, _('Foaming solution')),
    (54, _('Alcohol solution')),
    (55, _('Ear solution')),
    (56, _('Solution')),
    (57, _('Gingival solution')),

    (90, _('Bottle')),
    (91, _('Flacon')),
    (92, _('Device')),
    (93, _('Adhesive skin dressing')),
    (94, _('Unidose')),

    (100, _('Single-dose eye drops')),
    (101, _('Eye drops bottle')),
    (102, _('Collutory')),
    (103, _('Ophthalmic ointment'))
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
