# encoding: utf-8

from django import forms
from django.forms.models import modelformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset

from core.models import Person
from core.utils import horizontal_form_helper, format_datetime, indented_without_label, make_horizontal_form_helper

from .models import Programme, Role, Category, Room, Tag, AllRoomsPseudoView, START_TIME_LABEL


class ProgrammeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if 'self_service' in kwargs:
            self_service = kwargs.pop('self_service')
        else:
            self_service = False

        super(ProgrammeForm, self).__init__(*args, **kwargs)
        self.helper = horizontal_form_helper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(u'Ohjelmanumeron julkiset tiedot',
                'title',
                'description',
            ),
        )

    class Meta:
        model = Programme
        fields = (
            'title',
            'description',
        )


class ProgrammeExtraForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if 'self_service' in kwargs:
            self_service = kwargs.pop('self_service')
        else:
            self_service = False

        super(ProgrammeExtraForm, self).__init__(*args, **kwargs)
        self.helper = horizontal_form_helper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(u'Järjestäjien tarvitsemat lisätiedot',
                'room_requirements',
                'tech_requirements',
                'requested_time_slot',
                'video_permission',
                'notes_from_host',
            ),
        )

        if self_service:
            for field_name in [
                'room_requirements',
                'tech_requirements',
                'requested_time_slot',
            ]:
                self.fields[field_name].required = True

    class Meta:
        model = Programme
        fields = (
            'room_requirements',
            'tech_requirements',
            'requested_time_slot',
            'video_permission',
            'notes_from_host',
        )


class ProgrammePersonFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ProgrammePersonFormHelper, self).__init__(*args, **kwargs)
        make_horizontal_form_helper(self)
        self.form_tag = False
        self.layout = Layout(
            'first_name',
            'surname',
            'nick',
            'preferred_name_display_style',
            'phone',
            'email',
            indented_without_label('may_send_info'),
        )


class ProgrammePersonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProgrammePersonForm, self).__init__(*args, **kwargs)
        self.helper = ProgrammePersonFormHelper()

    class Meta:
        model = Person
        fields = [
            'email',
            'first_name',
            'may_send_info',
            'nick',
            'phone',
            'preferred_name_display_style',
            'surname',
        ]


class SelfServiceProgrammePersonForm(ProgrammePersonForm):
    def __init__(self, *args, **kwargs):
        super(SelfServiceProgrammePersonForm, self).__init__(*args, **kwargs)

        for field_name in [
            'email',
            'phone'
        ]:
            self.fields[field_name].required = True


AdminProgrammePersonFormSet = modelformset_factory(Person,
    form=ProgrammePersonForm,
    can_delete=True,
    can_order=False,
    extra=1
)

SelfServiceProgrammePersonFormSet = modelformset_factory(Person,
    form=SelfServiceProgrammePersonForm,
    can_delete=False,
    can_order=False,
    extra=0
)

class ProgrammeAdminForm(forms.ModelForm):
    # XXX
    start_time = forms.ChoiceField(choices=[], label=START_TIME_LABEL, required=False)

    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')

        super(ProgrammeAdminForm, self).__init__(*args, **kwargs)
        self.helper = horizontal_form_helper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(u'Ohjelmavastaavan merkinnät (eivät näy ohjelmanjärjestäjälle)',
                'state',
                'category',
                'room',
                'start_time',
                'length',
                'tags',
                'notes',
            ),
        )

        self.fields['length'].widget.attrs['min'] = 0
        self.fields['category'].queryset = Category.objects.filter(event=event)
        self.fields['room'].queryset = Room.objects.filter(venue=event.venue)
        self.fields['tags'].queryset = Tag.objects.filter(event=event)

        # XXX
        self.fields['start_time'].choices = [('', u'---------')] + [
            (
                start_time,
                format_datetime(start_time)
            ) for start_time in AllRoomsPseudoView(event).start_times()
        ]

    def clean_room(self):
        room = self.cleaned_data['room']

        if state == 'published' and room is None:
            raise ValidationError(u'Julkaistulle ohjelmalle täytyy määrittää tila.')
        elif state in ['rejected', 'cancelled'] and room is not None:
            raise ValidationError(u'Siivoa itte huonees hylätyistä ja piilotetuista ohjelmista!')

        return room

    def clean_start_time(self):
        start_time = self.cleaned_data['start_time']

        room = self.cleaned_data['room']
        state = self.cleaned_data['state']

        if start_time == '':
            start_time = None

        if state == 'published' and start_time is None:
            raise ValidationError(u'Julkaistulla ohjelmalla täytyy olla alkuaika.')
        elif state in ['rejected', 'cancelled'] and start_time is not None:
            raise ValidationError(u'Hylätyllä tai peruutetulla ohjelmalla ei saa olla alkuaikaa.')

        if room is not None and start_time is None:
            raise ValidationError(u'Jos tila on asetettu, myös alkuaika tulee asettaa.')

        return start_time

    def clean_length(self):
        length = self.cleaned_data['length']

        room = self.cleaned_data['room']
        start_time = self.cleaned_data['start_time']
        state = self.cleaned_data['state']

        if length is None:
            if state == 'published':
                raise ValidationError(u'Julkaistulla ohjelmalla täytyy olla pituus.')
            elif room is not None:
                raise ValidationError(u'Jos tila on asetettu, myös pituus tulee asettaa.')
            elif start_time is not None:
                raise ValidationError(u'Jos alkuaika on asetettu, myös pituus tulee asettaa.')
        else:
            if state in ['rejected', 'cancelled']:
                raise ValidationError(u'Hylätyllä tai peruutetulla ohjelmalla ei saa olla pituutta.')

        return length

    class Meta:
        model = Programme
        fields = (
            'category',
            'length',
            'notes',
            'room',
            'start_time',
            'state',
            'tags',
        )

        widgets = dict(
            tags=forms.CheckboxSelectMultiple,
        )
