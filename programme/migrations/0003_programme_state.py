# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programme', '0002_auto_20150115_1949'),
    ]

    operations = [
        migrations.AddField(
            model_name='programme',
            name='state',
            field=models.CharField(default=b'published', help_text='Tilassa "Julkaistu" olevat ohjelmat n\xe4kyv\xe4t ohjelmakartassa, jos ohjelmakartta on julkinen.', max_length=15, verbose_name='Ohjelmanumeron tila', choices=[('idea', 'Ideoitu sis\xe4isti'), ('asked', 'Kysytty ohjelmanj\xe4rjest\xe4j\xe4lt\xe4'), ('offered', 'Ohjelmatarjous vastaanotettu'), ('accepted', 'Hyv\xe4ksytty'), ('published', 'Julkaistu'), ('cancelled', 'Peruutettu'), ('rejected', 'Hyl\xe4tty')]),
            preserve_default=True,
        ),
    ]
