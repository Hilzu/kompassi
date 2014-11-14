# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def populate_core_signup(apps, schema_editor):
    Badge = apps.get_model('badges', 'Badge')
    CoreSignup = apps.get_model('core', 'Signup')
    LabourSignup = apps.get_model('labour', 'Signup')
    PersonnelClass = apps.get_model('core', 'PersonnelClass')

    for labour_signup in LabourSignup.objects.all():
        event = labour_signup.event
        person = labour_signup.person

        try:
            badge = Badge.objects.get(template__event=event, person=person)
        except Badge.DoesNotExist:
            personnel_class, unused = PersonnelClass.objects.get_or_create(
                event=event,
                slug='tyovoima',
                defaults=dict(
                    app_label='labour',
                    name=u'Työvoima',
                )
            )
        else:
            personnel_class, unused = PersonnelClass.objects.get_or_create(
                event=event,
                slug=badge.template.slug,
                defaults=dict(
                    app_label='labour',
                    name=badge.template.name,
                )
            )

        core_signup = CoreSignup.objects.create(
            person=person,
            personnel_class=personnel_class,
            is_active=labour_signup.is_active,
        )

        labour_signup.core_signup = core_signup
        labour_signup.save()


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0001_initial'),
        ('labour', '0002_signup_core_signup'),
    ]

    operations = [
        migrations.RunPython(populate_core_signup)
    ]
