# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-10 07:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0029_nullable_app_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appstatusformstaging',
            name='app_dim',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='warehouse.ApplicationDim'),
        ),
    ]