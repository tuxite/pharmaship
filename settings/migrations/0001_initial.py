# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.core.validators

def addVessel(apps, schema_editor):
    # Adds default vessel to the database
    Location = apps.get_model("settings", "Vessel")
    db_alias = schema_editor.connection.alias
    Location.objects.using(db_alias).bulk_create([
        Location(pk=1, 
                 name="My Vessel",
                 imo=0,
                 mmsi=0,
                 call_sign="",
                 flag="",
                 shipowner="",
                 port_of_registry="",
                 email="",
                 sat_phone="",
                 gsm_phone="", 
                 ),
    ])

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')])),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('function', models.CharField(blank=True, max_length=2, null=True, verbose_name='Function', choices=[('00', b'Captain'), ('10', b'Chief Officer'), ('11', b'Deck Officer'), ('20', b'Chief Engineer'), ('21', b'Engineer'), ('99', b'Ratings')])),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name='Name')),
                ('department', models.CharField(blank=True, max_length=1, null=True, verbose_name='Department', choices=[('D', b'Deck'), ('E', b'Engine'), ('C', b'Civil')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vessel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name='Name')),
                ('imo', models.IntegerField(max_length=7, verbose_name=b'IMO')),
                ('call_sign', models.CharField(max_length=30, verbose_name='Call Sign')),
                ('sat_phone', models.CharField(max_length=20)),
                ('gsm_phone', models.CharField(max_length=20)),
                ('flag', models.CharField(max_length=30, verbose_name='Flag')),
                ('port_of_registry', models.CharField(max_length=100, verbose_name='Port of Registry')),
                ('shipowner', models.CharField(max_length=100, verbose_name='Shipowner')),
                ('mmsi', models.IntegerField(max_length=9, verbose_name=b'MMSI')),
                ('fax', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=64)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(addVessel),
    ]
