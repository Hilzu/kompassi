# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-16 16:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0009_accom_limit_group_refactor'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='requires_shirt_size',
            field=models.BooleanField(default=False),
        ),
    ]
