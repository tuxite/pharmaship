# Generated by Django 3.2 on 2021-04-30 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_item_packing'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='name_en',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='equipment',
            name='name_fr',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='equipment',
            name='packaging_en',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='equipment',
            name='packaging_fr',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='equipment',
            name='remark_en',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='equipment',
            name='remark_fr',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='allowance',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='article',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='equipmentgroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='equipmentreqqty',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='firstaidkit',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='firstaidkititem',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='firstaidkitreqqty',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='laboratoryreqqty',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='location',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='medicine',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='molecule',
            name='dosage_form',
            field=models.IntegerField(choices=[(1, 'Tablet'), (2, 'Ampoule'), (3, 'Capsule'), (5, 'Oral Lyophilisate'), (6, 'Sachet'), (7, 'Suppository'), (8, 'Vial'), (9, 'Powder'), (10, 'Tube pommade'), (11, 'Tube crème'), (12, 'Gel buccal'), (13, 'Unidose gel'), (40, 'Seringue pré-remplie'), (50, 'Solution pour perfusion'), (51, 'Solution injectable'), (52, 'Solution acqueuse'), (53, 'Solution moussante'), (54, 'Solution alcoolisée'), (55, 'Solution auriculaire'), (56, 'Solution'), (57, 'Solution gingivale'), (90, 'Bottle'), (91, 'Flacon'), (92, 'Dispositif'), (93, 'Pansement adhésif cutané'), (94, 'Unidose'), (100, 'Collyre unidose'), (101, 'Collyre flacon'), (102, 'Collutoire'), (103, 'Pommade ophtalmique')]),
        ),
        migrations.AlterField(
            model_name='molecule',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='moleculegroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='moleculereqqty',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='qtytransaction',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='rescuebag',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='rescuebagreqqty',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='telemedicalreqqty',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AddField(
            model_name='equipmentgroup',
            name='name_en',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='equipmentgroup',
            name='name_fr',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='molecule',
            name='composition_en',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='molecule',
            name='composition_fr',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='molecule',
            name='name_en',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='molecule',
            name='name_fr',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='molecule',
            name='remark_en',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='molecule',
            name='remark_fr',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='moleculegroup',
            name='name_en',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='moleculegroup',
            name='name_fr',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterModelOptions(
            name='equipmentgroup',
            options={'ordering': ('order', 'name_en')},
        ),
        migrations.AlterUniqueTogether(
            name='equipment',
            unique_together={('name_en', 'packaging_en', 'consumable', 'perishable')},
        ),
        migrations.AlterUniqueTogether(
            name='equipmentgroup',
            unique_together={('name_en',)},
        ),
        migrations.AlterUniqueTogether(
            name='molecule',
            unique_together={('name_en', 'roa', 'dosage_form', 'composition_en')},
        ),
        migrations.AlterModelOptions(
            name='moleculegroup',
            options={'ordering': ('order', 'name_en')},
        ),
        migrations.AlterUniqueTogether(
            name='moleculegroup',
            unique_together={('name_en',)},
        ),
        migrations.AlterField(
            model_name='molecule',
            name='dosage_form',
            field=models.IntegerField(choices=[(1, 'Tablet'), (2, 'Ampoule'), (3, 'Capsule'), (5, 'Oral Lyophilisate'), (6, 'Sachet'), (7, 'Suppository'), (8, 'Vial'), (9, 'Powder'), (10, 'Ointment tube'), (11, 'Cream tube'), (12, 'Oral gel'), (13, 'Unidose gel'), (40, 'Pre-filled syringe'), (50, 'Solution for infusion'), (51, 'Solution for injection'), (52, 'Aqueous solution'), (53, 'Foaming solution'), (54, 'Alcohol solution'), (55, 'Ear solution'), (56, 'Solution'), (57, 'Gingival solution'), (90, 'Bottle'), (91, 'Flacon'), (92, 'Device'), (93, 'Adhesive skin dressing'), (94, 'Unidose'), (100, 'Single-dose eye drops'), (101, 'Eye drops bottle'), (102, 'Collutory'), (103, 'Ophthalmic ointment')]),
        ),
    ]
