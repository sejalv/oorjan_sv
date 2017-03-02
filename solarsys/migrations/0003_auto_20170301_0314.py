# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-28 21:44
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solarsys', '0002_auto_20170228_0219'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.DecimalField(decimal_places=6, max_digits=9)),
                ('long', models.DecimalField(decimal_places=6, max_digits=9)),
                ('system_capacity', models.DecimalField(decimal_places=3, max_digits=9)),
                ('dc', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),
        migrations.RenameModel(
            old_name='Home',
            new_name='InstallationKey',
        ),
        migrations.RemoveField(
            model_name='referencedc',
            name='installation_id',
        ),
        migrations.DeleteModel(
            name='SolarReference',
        ),
        migrations.AlterField(
            model_name='livedc',
            name='dc_power',
            field=models.DecimalField(decimal_places=4, max_digits=9),
        ),
        migrations.DeleteModel(
            name='Installation',
        ),
        migrations.DeleteModel(
            name='ReferenceDC',
        ),
    ]
