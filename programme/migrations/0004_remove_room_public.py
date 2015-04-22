# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programme', '0003_programme_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='public',
        ),
    ]
