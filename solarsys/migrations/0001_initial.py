# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-08 02:41
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InstallationKey',
            fields=[
                ('installation_key', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('lat', models.DecimalField(decimal_places=6, max_digits=9)),
                ('long', models.DecimalField(decimal_places=6, max_digits=9)),
                ('system_capacity', models.DecimalField(decimal_places=4, max_digits=7)),
                ('address', models.CharField(blank=True, default='', max_length=255)),
                ('added_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='LiveDC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('dc_power', models.DecimalField(decimal_places=4, max_digits=9)),
                ('installation_key', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='solarsys.InstallationKey')),
            ],
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.DecimalField(decimal_places=6, max_digits=9)),
                ('long', models.DecimalField(decimal_places=6, max_digits=9)),
                ('system_capacity', models.DecimalField(decimal_places=3, max_digits=9)),
                ('dc', django.contrib.postgres.fields.jsonb.JSONField()),
                ('added_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='installationkey',
            name='installation_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='solarsys.Reference'),
        ),
    ]
