# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def addTags(apps, schema_editor):
    # Adds default tags to the database
    Tag = apps.get_model("inventory", "Tag")
    db_alias = schema_editor.connection.alias
    Tag.objects.using(db_alias).bulk_create([
        Tag(pk=1, name="Usage courant"),
        Tag(pk=2, name="Conservation au froid")
    ])

def addGroups(apps, schema_editor):
    # Adds default groups to the database
    MoleculeGroup = apps.get_model("inventory", "MoleculeGroup")
    EquipmentGroup = apps.get_model("inventory", "EquipmentGroup")
    db_alias = schema_editor.connection.alias
    MoleculeGroup.objects.using(db_alias).bulk_create([
        MoleculeGroup(pk=1, name="Cardiologie", order=1),
        MoleculeGroup(pk=2, name="Gastro-Entérologie", order=2),
        MoleculeGroup(pk=3, name="Antalgiques Antipyrétiques Antispasmodiques Anti-inflammatoires", order=3),
        MoleculeGroup(pk=4, name="Psychatrie - Neurologie", order=4),
        MoleculeGroup(pk=5, name="Allergologie", order=5),
        MoleculeGroup(pk=6, name="Pneumologie", order=6),
        MoleculeGroup(pk=7, name="Infectiologie - Parasitologie", order=7),
        MoleculeGroup(pk=8, name="Réanimation", order=8),
        MoleculeGroup(pk=9, name="Dermatologie", order=9),
        MoleculeGroup(pk=10, name="Ophtalmologie", order=10),
        MoleculeGroup(pk=11, name="Oto-Rhino-Laryngologie - Stomatologie", order=11),
        MoleculeGroup(pk=12, name="Anésthésiques locaux", order=12),
    ])
    EquipmentGroup.objects.using(db_alias).bulk_create([
        EquipmentGroup(pk=1, name="Matériel de réanimation", order=1),
        EquipmentGroup(pk=2, name="Pansements et matériel de suture", order=2),
        EquipmentGroup(pk=3, name="Instruments", order=3),
        EquipmentGroup(pk=4, name="Matériel d'examen et de surveillance médicale", order=4),
        EquipmentGroup(pk=5, name="Matériel d'injection, de perfusion, de ponction et de sondage", order=5),
        EquipmentGroup(pk=6, name="Matériel médical général", order=6),
        EquipmentGroup(pk=7, name="Matériel d'immobilisation et de contention", order=7),
        EquipmentGroup(pk=8, name="Désinfection  - Désinsectisation - Protection", order=8),
        EquipmentGroup(pk=9, name="Matériel de téléconsultation cardiologique", order=9),
        EquipmentGroup(pk=10, name="Trousse de Premiers Secours", order=10),
    ])

def addAllowance(apps, schema_editor):
    # Adds default allowance to the database
    Allowance = apps.get_model("inventory", "Allowance")
    db_alias = schema_editor.connection.alias
    Allowance.objects.using(db_alias).bulk_create([
        Allowance(pk=1, name="Hors dotation", additional=False),
    ])
    
def addLocation(apps, schema_editor):
    # Adds default locations to the database
    Location = apps.get_model("inventory", "Location")
    db_alias = schema_editor.connection.alias
    Location.objects.using(db_alias).bulk_create([
        Location(pk=1, primary="Pharmacy", secondary=""),
    ])
     
def addSettings(apps, schema_editor):
    # Adds default locations to the database
    Settings = apps.get_model("inventory", "Settings")
    Allowance = apps.get_model("inventory", "Allowance")
    db_alias = schema_editor.connection.alias
    Settings.objects.using(db_alias).bulk_create([
        Settings(pk=1, expire_date_warning_delay=70),
    ]) 
    Settings.objects.get(pk=1).allowance.add(Allowance.objects.get(pk=1))
    
class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allowance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('additional', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date', blank=True)),
                ('nc_packaging', models.CharField(max_length=100, null=True, verbose_name='Non-conform Packaging', blank=True)),
                ('used', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('exp_date',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('packaging', models.CharField(max_length=100)),
                ('consumable', models.BooleanField(default=False)),
                ('perishable', models.BooleanField(default=False)),
                ('picture', models.ImageField(null=True, upload_to=b'pictures', blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EquipmentGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('order', models.IntegerField()),
            ],
            options={
                'ordering': ('order', 'name'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EquipmentReqQty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('required_quantity', models.IntegerField()),
                ('allowance', models.ForeignKey(to='inventory.Allowance')),
                ('base', models.ForeignKey(to='inventory.Equipment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('primary', models.CharField(max_length=100, verbose_name='Primary')),
                ('secondary', models.CharField(max_length=100, null=True, verbose_name='Secondary', blank=True)),
            ],
            options={
                'ordering': ('primary', 'secondary'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Medicine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('exp_date', models.DateField(verbose_name='Expiration Date')),
                ('nc_molecule', models.CharField(max_length=100, null=True, verbose_name='Non-conform Molecule', blank=True)),
                ('nc_composition', models.CharField(max_length=100, null=True, verbose_name='Non-conform Composition', blank=True)),
                ('used', models.BooleanField(default=False)),
                ('location', models.ForeignKey(to='inventory.Location')),
            ],
            options={
                'ordering': ('exp_date',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Molecule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('roa', models.PositiveIntegerField(choices=[(1, b'Orale'), (5, b'Parent\xc3\xa9rale'), (6, b'Sous-cutann\xc3\xa9e'), (10, b'Locale'), (11, b'Transdermique'), (20, b'Inhalation'), (21, b'N\xc3\xa9bulisation'), (30, b'Buccale'), (31, b'Sublinguale'), (32, b'Bain de bouche'), (40, b'Rectale'), (41, b'Vaginale'), (50, b'Oculaire')])),
                ('dosage_form', models.IntegerField(choices=[(1, b'Comprim\xc3\xa9'), (2, b'Ampoule'), (3, b'G\xc3\xa9lule'), (5, b'Lyophilisat oral'), (6, b'Sachet'), (7, b'Suppositoire'), (8, b'Capsule'), (10, b'Tube pommade'), (11, b'Tube cr\xc3\xa8me'), (12, b'Gel buccal'), (13, b'Unidose gel'), (40, b'Seringue pr\xc3\xa9-remplie'), (50, b'Solution pour perfusion'), (51, b'Solution injectable'), (52, b'Solution acqueuse'), (53, b'Solution moussante'), (54, b'Solution alcoolis\xc3\xa9e'), (55, b'Solution auriculaire'), (56, b'Solution'), (90, b'Bouteille'), (91, b'Flacon'), (92, b'Dispositif'), (93, b'Pansement adh\xc3\xa9sif cutan\xc3\xa9'), (94, b'Unidose'), (100, b'Collyre unidose'), (101, b'Collyre flacon'), (102, b'Collutoire'), (103, b'Pommade ophtalmique')])),
                ('composition', models.CharField(max_length=100)),
                ('medicine_list', models.PositiveIntegerField(choices=[(0, b'None'), (1, b'Liste I'), (2, b'Liste II'), (9, b'Stup\xc3\xa9fiants')])),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MoleculeGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('order', models.IntegerField()),
            ],
            options={
                'ordering': ('order', 'name'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MoleculeReqQty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('required_quantity', models.IntegerField()),
                ('allowance', models.ForeignKey(to='inventory.Allowance')),
                ('base', models.ForeignKey(to='inventory.Molecule')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QtyTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transaction_type', models.PositiveIntegerField(verbose_name='Type', choices=[(1, b'In'), (2, b'Utilis\xc3\xa9'), (4, b'P\xc3\xa9rim\xc3\xa9'), (8, b'Physical Count'), (9, b'Other')])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('remark', models.TextField(null=True, blank=True)),
                ('value', models.IntegerField(verbose_name='Value')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Remark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(null=True, verbose_name='Text', blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('expire_date_warning_delay', models.PositiveIntegerField(verbose_name='Warning Delay for Expiration Dates')),
                ('allowance', models.ManyToManyField(to='inventory.Allowance', verbose_name='Allowance')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('comment', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('name',)]),
        ),
        migrations.AlterUniqueTogether(
            name='moleculegroup',
            unique_together=set([('name',)]),
        ),
        migrations.AddField(
            model_name='molecule',
            name='allowances',
            field=models.ManyToManyField(to='inventory.Allowance', through='inventory.MoleculeReqQty'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='molecule',
            name='group',
            field=models.ForeignKey(to='inventory.MoleculeGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='molecule',
            name='tag',
            field=models.ManyToManyField(to='inventory.Tag', blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='molecule',
            unique_together=set([('name', 'roa', 'dosage_form', 'composition')]),
        ),
        migrations.AddField(
            model_name='medicine',
            name='parent',
            field=models.ForeignKey(to='inventory.Molecule'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='equipmentgroup',
            unique_together=set([('name',)]),
        ),
        migrations.AddField(
            model_name='equipment',
            name='allowances',
            field=models.ManyToManyField(to='inventory.Allowance', through='inventory.EquipmentReqQty'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='equipment',
            name='group',
            field=models.ForeignKey(to='inventory.EquipmentGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='equipment',
            name='tag',
            field=models.ManyToManyField(to='inventory.Tag', blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='equipment',
            unique_together=set([('name', 'packaging', 'consumable', 'perishable', 'group')]),
        ),
        migrations.AddField(
            model_name='article',
            name='location',
            field=models.ForeignKey(to='inventory.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='parent',
            field=models.ForeignKey(to='inventory.Equipment'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='allowance',
            unique_together=set([('name',)]),
        ),
        migrations.RunPython(addTags),
        migrations.RunPython(addGroups),
        migrations.RunPython(addAllowance),
        migrations.RunPython(addLocation),
        migrations.RunPython(addSettings),
    ]
