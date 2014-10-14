# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20141014_2240'),
        ('labour', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='signup',
            name='core_signup',
            field=models.ForeignKey(blank=True, to='core.Signup', null=True),
            preserve_default=True,
        ),
    ]
