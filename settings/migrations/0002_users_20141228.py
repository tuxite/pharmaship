# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings

import settings.utils as utils

def addRank(apps, schema_editor):
    # Adds default tags to the database
    Rank = apps.get_model("settings", "Rank")
    db_alias = schema_editor.connection.alias
    Rank.objects.using(db_alias).bulk_create([
        Rank(pk=1, name="Crew", priority=99, groups="[]"),
    ])

class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mouvement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=datetime.date.today())),
                ('position', models.BooleanField(default=None)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='user',
            name='function',
        ),
        migrations.AddField(
            model_name='rank',
            name='groups',
            field=models.CharField(default=datetime.date.today(), max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rank',
            name='priority',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),

	migrations.RunPython(addRank),

        migrations.AddField(
            model_name='user',
            name='birth_date',
            field=models.DateField(default=datetime.date(1970, 01, 01)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='birth_place',
            field=models.CharField(default='Unknown', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='company_id',
            field=models.CharField(max_length=64, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='nationality',
            field=models.CharField(default='Unknown', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='passport_expiry',
            field=models.DateField(default=datetime.date.today()),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='passport_number',
            field=models.CharField(default='Unknown', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='picture',
            field=models.ImageField(null=True, upload_to=utils.filepath, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='rank',
            field=models.ForeignKey(default=1, to='settings.Rank'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='seaman_book_expiry',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='seaman_book_number',
            field=models.CharField(default='Unknown', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='sex',
            field=models.CharField(default='M', max_length=1, choices=[('M', 'Male'), ('F', 'Female')]),
            preserve_default=False,
        ),

    ]
