# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-01 13:29
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('solarsys', '0004_auto_20170301_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='dc',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
    ]
