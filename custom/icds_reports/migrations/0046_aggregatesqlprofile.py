# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-24 08:47
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('icds_reports', '0045_add_new_wasting_stunting_to_chm'),
    ]

    operations = [
        migrations.CreateModel(
            name='AggregateSQLProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('date', models.DateField(auto_now=True)),
                ('duration', models.PositiveIntegerField()),
            ],
        ),
    ]
