# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('quantity', models.PositiveIntegerField()),
                ('additional', models.TextField(null=True, blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Requisition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('reference', models.CharField(max_length=20)),
                ('date_of_creation', models.DateTimeField(auto_now_add=True)),
                ('requested_date', models.DateField(null=True, blank=True)),
                ('status', models.PositiveIntegerField(verbose_name='Status', choices=[(0, b'Draft'), (1, b'Pending Approval'), (2, b'Approved'), (3, b'Quoted'), (4, b'Ordered'), (5, b'Partially Received'), (6, b'Fully Received'), (99, b'Cancelled')])),
                ('instructions', models.TextField(null=True, blank=True)),
                ('port_of_delivery', models.CharField(max_length=5)),
                ('item_type', models.PositiveIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='item',
            name='requisition',
            field=models.ForeignKey(to='purchase.Requisition'),
            preserve_default=True,
        ),
    ]
