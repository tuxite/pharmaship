# -*- coding: utf-8; -*-
"""Inventory application models."""
from django.db import models
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from mptt.models import MPTTModel, TreeForeignKey

from pharmaship.inventory import constants
from pharmaship.inventory import utils

from pharmaship.core.utils import log


# Create your models here.
class Allowance(models.Model):
    """Model for articles and medicines allowances."""

    name = models.CharField(max_length=100)  # Example: Dotation A
    author = models.CharField(max_length=100)  # Example: CCMM Purpan
    signature = models.CharField(max_length=200)
    date = models.DateField()
    version = models.CharField(max_length=20)
    # For use with complements.
    # True will add quantity, false will be treated as an absolute quantity.
    additional = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    def __str__(self):  # noqa: D105
        """Return human readable name and version of the Allowance instance."""
        return "{0} ({1})".format(self.name, self.version)

    class Meta:  # noqa: D106
        unique_together = ('name', )


class GroupManager(models.Manager):
    """Manager for class MedicineGroup and MaterialGroup.

    For deserialization purpose only.
    """

    def get_by_natural_key(self, name_en):
        return self.get(name_en=name_en)


class MoleculeGroup(models.Model):
    """Model for groups attached to a :mod:`pharmaship.inventory.models.Molecule` instance."""

    objects = GroupManager()  # For deserialization

    name = models.CharField(max_length=100)  # Example: Cardiology
    order = models.IntegerField()  # Example: 1

    def __str__(self):  # noqa: D105
        return "{0}. {1}".format(self.order, _(self.name))

    def natural_key(self):
        return (self.name_en,)

    class Meta:  # noqa: D106
        ordering = ("order", "name_en",)
        unique_together = ('name_en', )


class EquipmentGroup(models.Model):
    """Model for groups attached to a :mod:`pharmaship.inventory.models.Equipment` instance."""

    objects = GroupManager()  # For deserialization

    name = models.CharField(max_length=100)  # Example: Reanimation
    order = models.IntegerField()  # Example: 1

    def __str__(self):  # noqa: D105
        return "{0}. {1}".format(self.order, _(self.name))

    def natural_key(self):
        return (self.name_en,)

    class Meta:  # noqa: D106
        ordering = ("order", "name_en",)
        unique_together = ('name_en', )


class TagManager(models.Manager):
    """Manager for class Tag.

    For deserialization purpose only.
    """

    def get_by_natural_key(self, name):
        return self.get(name=name)


class Tag(models.Model):
    """Stores tags attached to a :mod:`pharmaship.inventory.models.Equipment` or
    model:`pharmaship.inventory.models.Molecule` instance.
    """

    objects = TagManager()  # For deserialization

    name = models.CharField(max_length=100)  # Example: Common Use
    comment = models.TextField(blank=True, null=True)  # Description of the tag

    def __str__(self):  # noqa: D105
        return _(self.name)

    def natural_key(self):
        return (self.name,)

    class Meta:  # noqa: D106
        ordering = ("name",)
        unique_together = ('name',)


class Location(MPTTModel):
    """Stores locations attached to a :mod:`pharmaship.inventory.models.Equipment` or
    model:`pharmaship.inventory.models.Molecule` instance.
    """

    name = models.CharField(_("Name"), max_length=100)
    parent = TreeForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    is_rescue_bag = models.BooleanField(default=False)

    def __str__(self):  # noqa: D105
        return _(self.name)

    class MPTTMeta:  # noqa: D106
        order_insertion_by = ['name']


class QtyTransaction(models.Model):
    """Stores a quantity transaction related to :mod:`pharmaship.inventory.models.Article`
    or :mod:`pharmaship.inventory.models.Medicine`.

    There are 5 types of transactions:
    * 1 IN: a material is added,
    * 2 USED: the material is used for a treatment,
    * 4 PERISHED: the material has expired,
    * 8 PHYSICAL_COUNT: the stock is refreshed after a human count,
    * 9 OTHER: other reason.
    """

    transaction_type = models.PositiveIntegerField(_("Type"), choices=constants.TRANSACTION_TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    remark = models.TextField(blank=True, null=True)
    value = models.IntegerField(_("Value"), )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):  # noqa: D105
        return "{0} ({1}: {2})".format(self.content_object, self.get_transaction_type_display(), self.value)


class BaseItem(models.Model):
    name = models.CharField(_("Name"), max_length=100)  # Brand Name. Example: Doliprane for INN Paracétamol
    exp_date = models.DateField(_("Expiration Date"), blank=True, null=True)
    used = models.BooleanField(default=False)
    transactions = GenericRelation(QtyTransaction, related_query_name='transactions')
    remark = models.CharField(_("Remark"), max_length=256, blank=True, null=True)

    # Packing
    packing_content = models.PositiveIntegerField(_("Quantity per pack"), default=1)
    packing_name = models.PositiveIntegerField(choices=constants.PACKING_CHOICES, default=0)

    def __str__(self):  # noqa: D105
        return "{0} (exp: {1})".format(self.name, self.exp_date)

    def get_quantity(self):
        """Compute the quantity according to the transactions attached to this medicine."""
        # Get latest Stock Count and then make the sum
        transactions = self.transactions.order_by("date")

        # Find last IN (type=1) or STOCK COUNT (type=8)
        last_stock_count = transactions.filter(transaction_type__in=[1, 8]).latest("date")
        # If found: filter by date (only recent transaction to take in account)
        # If not found: start from beginning
        if last_stock_count:
            transactions = self.transactions.filter(date__gte=last_stock_count.date).order_by("date")
        # Parse each transactions
        quantity = 0
        for transaction in transactions:
            if transaction.transaction_type in [1, 8]:
                quantity = transaction.value
            else:
                quantity -= transaction.value

        if quantity < 0:
            log.warning("Element with negative quantity")
            return 0
        return quantity

    class Meta:  # noqa: D106
        abstract = True
        ordering = ("exp_date", )


class BaseChestItem(BaseItem):
    # Link to location
    location = models.ForeignKey(Location, on_delete=models.SET_DEFAULT, default=0)

    class Meta:  # noqa: D106
        abstract = True


class BaseReqQty(models.Model):
    """Model for required quantity of a medical equipment"""

    allowance = models.ForeignKey('Allowance', on_delete=models.CASCADE)
    required_quantity = models.IntegerField()

    class Meta:  # noqa: D106
        abstract = True


class MoleculeManager(models.Manager):
    """Manager for :mod:`pharmaship.inventory.models.Molecule`."""

    def get_by_natural_key(self, name_en, roa, dosage_form, composition_en):
        return self.get(
            name=name_en,
            roa=roa,
            dosage_form=dosage_form,
            composition=composition_en
            )


class Molecule(models.Model):
    """Store molecule objects used as referent in an
    :mod:`pharmaship.inventory.models.Allowance`.
    """

    objects = MoleculeManager()  # For deserialization

    name = models.CharField(max_length=100)  # Example: Paracétamol
    roa = models.PositiveIntegerField(choices=constants.DRUG_ROA_CHOICES)  # Example: dermal -- ROA: Route of Administration
    dosage_form = models.IntegerField(choices=constants.DRUG_FORM_CHOICES)  # Example: "pill"
    composition = models.CharField(max_length=100)  # Example: 1000 mg
    medicine_list = models.PositiveIntegerField(choices=constants.DRUG_LIST_CHOICES)  # Example: List I
    group = models.ForeignKey(MoleculeGroup, on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag, blank=True)
    allowances = models.ManyToManyField(Allowance, through='MoleculeReqQty')
    remark = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):  # noqa: D105
        return "{0} ({2} - {1})".format(self.name, self.composition, self.get_dosage_form_display())

    def natural_key(self):
        return (self.name_en, self.roa, self.dosage_form, self.composition_en)

    def order_info(self):
        """Output a string for Purchase application."""
        s = u"{0} {1} - {2} {3}".format(_("Dosage Form:"), self.get_dosage_form_display(), _("Composition:"), self.composition)
        return s

    class Meta:  # noqa: D106
        ordering = ('name', )
        unique_together = (('name_en', 'roa', 'dosage_form', 'composition_en'),)


class Medicine(BaseChestItem):
    """Stores a medicine object, "child" of :mod:`pharmaship.inventory.models.Molecule`."""

    parent = models.ForeignKey(Molecule, on_delete=models.CASCADE, related_name="medicines")
    # Fields for non-conformity compatibility
    nc_molecule = models.CharField(_("Non-conform Molecule"), max_length=100, blank=True, null=True)
    nc_composition = models.CharField(_("Non-conform Composition"), max_length=100, blank=True, null=True)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if self.exp_date is None:
            raise ValidationError({
                'exp_date': _('Expiry date must be provided.')
            })


class MoleculeReqQty(BaseReqQty):
    """Model for required quantity of a medicine"""
    base = models.ForeignKey('Molecule', on_delete=models.CASCADE)


class EquipmentManager(models.Manager):
    """Manager for class Equipment.

    For deserialization purpose only.
    """

    def get_by_natural_key(self, name_en, packaging_en, consumable, perishable):
        return self.get(
            name=name_en,
            packaging=packaging_en,
            consumable=consumable,
            perishable=perishable
            )


class Equipment(models.Model):
    """Model for medical equipment."""
    objects = EquipmentManager()  # For deserialization

    name = models.CharField(max_length=100)  # Example: Nébulisateur
    packaging = models.CharField(max_length=100)  # Example: 1000 mg
    group = models.ForeignKey(EquipmentGroup, on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag, blank=True)
    consumable = models.BooleanField(default=False)
    perishable = models.BooleanField(default=False)
    allowances = models.ManyToManyField(Allowance, through='EquipmentReqQty')
    remark = models.CharField(max_length=256, blank=True, null=True)
    picture = models.ImageField(upload_to=utils.filepath, blank=True, null=True)

    def __str__(self):  # noqa: D105
        return self.name

    def natural_key(self):
        return (self.name_en, self.packaging_en, self.consumable, self.perishable)

    def order_info(self):
        """Output a string for Purchase application."""
        s = u"{0} {1}".format(_("Packaging:"), self.packaging)
        return s

    class Meta:  # noqa: D106
        ordering = ('name', )
        unique_together = (('name_en', 'packaging_en', 'consumable', 'perishable'),)


class Article(BaseChestItem):
    """Article model, "child" of Equipment."""
    parent = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="articles")
    # Fields for non-conformity compatibility
    nc_packaging = models.CharField(_("Non-conform Packaging"), max_length=100, blank=True, null=True)


class EquipmentReqQty(BaseReqQty):
    """Model for required quantity of a medical equipment"""
    base = models.ForeignKey('Equipment', on_delete=models.CASCADE)


# class Settings(models.Model):
#     """Application settings."""
#     allowance = models.ManyToManyField(Allowance, verbose_name=_('Allowance'), blank=True)
#     expire_date_warning_delay = models.PositiveIntegerField(_("Warning Delay for Expiration Dates"), default=80)
#     has_laboratory = models.BooleanField(_("Equiped with laboratory?"), default=False)
#     has_telemedical = models.BooleanField(_("Equiped with telemedical equipment?"), default=False)
#     first_aid_kit = models.PositiveIntegerField(_("Number of first aid kits"), default=3)
#     rescue_bag = models.PositiveIntegerField(_("Number of rescue bags"), default=1)


class FirstAidKit(models.Model):
    """Model for First Aid Kits."""
    name = models.CharField(_("Name"), max_length=50)
    location = models.ForeignKey(Location, on_delete=models.SET_DEFAULT, default=0)

    def __str__(self):  # noqa: D105
        return self.name


class FirstAidKitReqQty(BaseReqQty):
    limit = models.Q(app_label='inventory', model='equipment') | models.Q(app_label='inventory', model='molecule')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limit)
    object_id = models.PositiveIntegerField()
    base = GenericForeignKey('content_type', 'object_id')


class FirstAidKitItem(BaseItem):
    kit = models.ForeignKey(
        FirstAidKit,
        on_delete=models.CASCADE,
        related_name="items"
        )
    nc = models.CharField(
        _("Non conformity"),
        max_length=256,
        blank=True,
        null=True
        )

    limit = models.Q(
        app_label='inventory',
        model__in=['equipment', 'molecule']
        )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=limit
        )
    object_id = models.PositiveIntegerField()
    parent = GenericForeignKey('content_type', 'object_id')


class RescueBag(models.Model):
    """Model for rescue bags."""

    name = models.CharField(_("Name"), max_length=50)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_DEFAULT,
        default=0
        )

    def __str__(self):  # noqa: D105
        return self.name


class RescueBagReqQty(BaseReqQty):
    limit = models.Q(
        app_label='inventory',
        model__in=['equipment', 'molecule']
        )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=limit
        )
    object_id = models.PositiveIntegerField()
    base = GenericForeignKey('content_type', 'object_id')


class TelemedicalReqQty(BaseReqQty):
    base = models.ForeignKey('Equipment', on_delete=models.CASCADE)


class LaboratoryReqQty(BaseReqQty):
    base = models.ForeignKey('Equipment', on_delete=models.CASCADE)
