# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Perk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.CharField(help_text='Tekninen nimi eli "slug" n\xe4kyy URL-osoitteissa. Sallittuja merkkej\xe4 ovat pienet kirjaimet, numerot ja v\xe4liviiva. Teknist\xe4 nime\xe4 ei voi muuttaa luomisen j\xe4lkeen.', max_length=63, verbose_name='Tekninen nimi', validators=[django.core.validators.RegexValidator(regex=b'[a-z0-9-]+', message='Tekninen nimi saa sis\xe4lt\xe4\xe4 vain pieni\xe4 kirjaimia, numeroita sek\xe4 v\xe4liviivoja.')])),
                ('name', models.CharField(max_length=63)),
                ('event', models.ForeignKey(to='core.Event')),
            ],
            options={
                'verbose_name': 'etu',
                'verbose_name_plural': 'edut',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PersonnelClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app_label', models.CharField(default=b'', max_length=63, blank=True)),
                ('name', models.CharField(max_length=63)),
                ('slug', models.CharField(help_text='Tekninen nimi eli "slug" n\xe4kyy URL-osoitteissa. Sallittuja merkkej\xe4 ovat pienet kirjaimet, numerot ja v\xe4liviiva. Teknist\xe4 nime\xe4 ei voi muuttaa luomisen j\xe4lkeen.', max_length=63, verbose_name='Tekninen nimi', validators=[django.core.validators.RegexValidator(regex=b'[a-z0-9-]+', message='Tekninen nimi saa sis\xe4lt\xe4\xe4 vain pieni\xe4 kirjaimia, numeroita sek\xe4 v\xe4liviivoja.')])),
                ('event', models.ForeignKey(to='core.Event')),
                ('perks', models.ManyToManyField(to='core.Perk', blank=True)),
            ],
            options={
                'verbose_name': 'henkil\xf6st\xf6luokka',
                'verbose_name_plural': 'henkil\xf6st\xf6luokat',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Signup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=True)),
                ('person', models.ForeignKey(related_name=b'core_signup_set', to='core.Person')),
                ('personnel_class', models.ForeignKey(to='core.PersonnelClass')),
            ],
            options={
                'verbose_name': 'ilmoittautuminen',
                'verbose_name_plural': 'ilmoittautumiset',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='signup',
            unique_together=set([('personnel_class', 'person')]),
        ),
        migrations.AlterUniqueTogether(
            name='personnelclass',
            unique_together=set([('event', 'slug')]),
        ),
        migrations.AlterUniqueTogether(
            name='perk',
            unique_together=set([('event', 'slug')]),
        ),
    ]
