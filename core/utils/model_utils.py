# encoding: utf-8

from __future__ import unicode_literals

from datetime import datetime, timedelta
from functools import wraps
from itertools import groupby
from random import randint
import json
import sys
import re

from django import forms
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models, connection
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.timezone import now
from django.template.loader import render_to_string

from dateutil.tz import tzlocal

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, Hidden


validate_slug = RegexValidator(
    regex=r'[a-z0-9-]+',
    message='Tekninen nimi saa sisältää vain pieniä kirjaimia, numeroita sekä väliviivoja.'
)


SLUG_FIELD_PARAMS = dict(
    max_length=255,
    unique=True,
    validators=[validate_slug],
    verbose_name='Tekninen nimi',
    help_text='Tekninen nimi eli "slug" näkyy URL-osoitteissa. Sallittuja '
        'merkkejä ovat pienet kirjaimet, numerot ja väliviiva. Teknistä nimeä ei voi '
        'muuttaa luomisen jälkeen.',
)
NONUNIQUE_SLUG_FIELD_PARAMS = dict(SLUG_FIELD_PARAMS, unique=False)


SLUGIFY_CHAR_MAP = {
  ' ': '-',
  '.': '-',
  '_': '-',
  'à': 'a',
  'á': 'a',
  'ä': 'a',
  'å': 'a',
  'è': 'e',
  'é': 'e',
  'ë': 'e',
  'ö': 'o',
  'ü': '',
}
SLUGIFY_FORBANNAD_RE = re.compile(r'[^a-z0-9-]', re.UNICODE)
SLUGIFY_MULTIDASH_RE = re.compile(r'-+', re.UNICODE)


def slugify(ustr):
    ustr = ustr.lower()
    ustr = ''.join(SLUGIFY_CHAR_MAP.get(c, c) for c in ustr)
    ustr = SLUGIFY_FORBANNAD_RE.sub('', ustr)
    ustr = SLUGIFY_MULTIDASH_RE.sub('-', ustr)
    return ustr


def get_postgresql_version_num():
    if not 'postgresql' in settings.DATABASES['default']['ENGINE']:
        return 0

    with connection.cursor() as cursor:
        cursor.execute('SHOW server_version_num')
        return int(cursor.fetchone()[0])


def get_previous_and_next(queryset, current):
      if not current.pk:
          return None, None

      # TODO inefficient, done using a list
      signups = list(queryset)

      previous_item = None
      candidate = None

      for next_item in signups + [None]:
          if candidate and candidate.pk == current.pk:
              return previous_item, next_item

          previous_item = candidate
          candidate = next_item

      return None, None
