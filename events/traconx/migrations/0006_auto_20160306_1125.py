# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-06 09:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('traconx', '0005_auto_20150521_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signupextra',
            name='signup',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='traconx_signup_extra', serialize=False, to='labour.Signup'),
        ),
    ]