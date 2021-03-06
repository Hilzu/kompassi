# encoding: utf-8

from django.db import models

from labour.models import ObsoleteSignupExtraBaseV1
from labour.querybuilder import QueryBuilder, add_prefix

from core.utils import validate_slug


SHIRT_SIZES = [
    (u'NO_SHIRT', u'Ei paitaa'),

    (u'XS', u'XS'),
    (u'S', u'S'),
    (u'M', u'M'),
    (u'L', u'L'),
    (u'XL', u'XL'),
    (u'XXL', u'XXL'),

    # (u'3XL', u'3XL'),
    # (u'4XL', u'4XL'),
    # (u'5XL', u'5XL'),

    # (u'LF_XS', u'XS Ladyfit'),
    # (u'LF_S', u'S Ladyfit'),
    # (u'LF_M', u'M Ladyfit'),
    # (u'LF_L', u'L Ladyfit'),
    # (u'LF_XL', u'XL Ladyfit'),
]


class SimpleChoice(models.Model):
    name = models.CharField(max_length=63)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class Night(SimpleChoice):
    pass


class SpecialDiet(SimpleChoice):
    pass


class SignupExtra(ObsoleteSignupExtraBaseV1):
    shirt_size = models.CharField(
        max_length=8,
        choices=SHIRT_SIZES,
        verbose_name=u'Paidan koko',
        help_text=u'Ajoissa ilmoittautuneet vänkärit saavat maksuttoman työvoimapaidan. '
            u'Kokotaulukot: <a href="http://www.bc-collection.eu/uploads/sizes/TU004.jpg" '
            u'target="_blank">unisex-paita</a>, <a href="http://www.bc-collection.eu/uploads/sizes/TW040.jpg" '
            u'target="_blank">ladyfit-paita</a>',
    )

    special_diet = models.ManyToManyField(
        SpecialDiet,
        blank=True,
        verbose_name=u'Erikoisruokavalio'
    )

    special_diet_other = models.TextField(
        blank=True,
        verbose_name=u'Muu erikoisruokavalio',
        help_text=u'Jos noudatat erikoisruokavaliota, jota ei ole yllä olevassa listassa, '
            u'ilmoita se tässä. Tapahtuman järjestäjä pyrkii ottamaan erikoisruokavaliot '
            u'huomioon, mutta kaikkia erikoisruokavalioita ei välttämättä pystytä järjestämään.'
    )

    needs_lodging = models.ManyToManyField(
        Night,
        blank=True,
        verbose_name=u'Majoitustarve lattiamajoituksessa',
        help_text=u'Vänkärinä saat tarvittaessa maksuttoman majoituksen lattiamajoituksessa. Merkitse tähän, minä öinä tarvitset lattiamajoitusta.',
    )

    prior_experience = models.TextField(
        blank=True,
        verbose_name=u'Työkokemus',
        help_text=u'Kerro tässä kentässä, jos sinulla on aiempaa kokemusta vastaavista '
            u'tehtävistä tai muuta sellaista työkokemusta, josta arvioit olevan hyötyä '
            u'hakemassasi tehtävässä.'
    )

    free_text = models.TextField(
        blank=True,
        verbose_name=u'Vapaa alue',
        help_text=u'Jos haluat sanoa hakemuksesi käsittelijöille jotain sellaista, jolle ei ole '
            u'omaa kenttää yllä, käytä tätä kenttää.'
    )

    @classmethod
    def get_form_class(cls):
        from .forms import SignupExtraForm
        return SignupExtraForm

    @staticmethod
    def get_query_class():
        raise NotImplementedError()
