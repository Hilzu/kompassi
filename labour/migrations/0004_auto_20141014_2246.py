# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('labour', '0003_populate_core_signup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='signup',
            name='event',
        ),
        migrations.RemoveField(
            model_name='signup',
            name='person',
        ),
        migrations.AlterField(
            model_name='signup',
            name='core_signup',
            field=models.ForeignKey(to='core.Signup'),
        ),
    ]
