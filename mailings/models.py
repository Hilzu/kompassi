# encoding: utf-8

from hashlib import sha1
import logging
from datetime import datetime, timedelta

from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save

from math import ceil

from django.conf import settings
from django.db import models
from django.template import Template, Context
from django.utils import timezone


logger = logging.getLogger('kompassi')
APP_LABEL_CHOICES = [
    ('labour', 'Työvoima')
]

DELAY_PER_MESSAGE_FRAGMENT_MILLIS = 350


class RecipientGroup(models.Model):
    event = models.ForeignKey('core.Event', verbose_name=u'Tapahtuma')
    app_label = models.CharField(max_length=63, choices=APP_LABEL_CHOICES, verbose_name=u'Sovellus')
    group = models.ForeignKey('auth.Group', verbose_name=u'Käyttäjäryhmä')
    verbose_name = models.CharField(max_length=63, verbose_name=u'Nimi')
    job_category = models.ForeignKey('labour.JobCategory', null=True, blank=True)

    def __unicode__(self):
        return u"{self.event.name}: {self.verbose_name}".format(self=self)

    @classmethod
    def update_for_job_category(cls, job_category):
        try:
            recipient_group = cls.objects.get(job_category=job_category)
        except cls.DoesNotExist:
            logger.warn('Job category %s/%s has no recipient group', job_category.event.slug, job_category.slug)
        else:
            recipient_group.verbose_name = job_category.name
            recipient_group.save()

    class Meta:
        verbose_name = u'vastaanottajaryhmä'
        verbose_name_plural = u'vastaanottajaryhmät'


CHANNEL_CHOICES = [
    ('email', 'Sähköposti'),
    ('sms', 'Tekstiviesti'),
]


class Message(models.Model):
    channel = models.CharField(
        max_length=5,
        verbose_name=u'Kanava',
        default=u'email',
        choices=CHANNEL_CHOICES,
    )
    recipient = models.ForeignKey(RecipientGroup, verbose_name=u'Vastaanottajaryhmä')

    subject_template = models.CharField(
        max_length=255,
        verbose_name=u'Otsikko',
        help_text=u'HUOM! Otsikko näkyy vastaanottajalle ainoastaan, jos viesti lähetetään '
            u'sähköpostitse. Tekstiviestillä lähetettäville viesteille otsikkoa käytetään '
            u'ainoastaan viestin tunnistamiseen sisäisesti.',
    )
    body_template = models.TextField(
        verbose_name=u'Viestin teksti',
        help_text=u'Teksti {{ signup.formatted_job_categories_accepted }} korvataan '
            u'listalla hyväksytyn vänkärin tehtäväalueista ja teksti '
            u'{{ signup.formatted_shifts }} korvataan vänkärin vuoroilla. '
            u'Käyttäessäsi näitä muotoilukoodeja laita ne omiksi kappaleikseen ts. reunusta ne tyhjillä riveillä.'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    expired_at = models.DateTimeField(blank=True, null=True)

    @property
    def is_sent(self):
        return self.sent_at is not None

    @property
    def is_expired(self):
        return self.expired_at is not None

    def send(self, recipients=None, resend=False):
        if not self.sent_at:
            self.sent_at = timezone.now()
            self.save()

        if 'background_tasks' in settings.INSTALLED_APPS:
            from mailings.tasks import message_send
            message_send.delay(
                self.pk,
                [person.pk for person in recipients] if recipients is not None else None,
                resend
            )
        else:
            self._send(recipients, resend)

    def _send(self, recipients, resend):
        from django.contrib.auth.models import User

        if recipients is None:
            recipients = [user.person for user in self.recipient.group.user_set.all()]

        delay = 0
        for person in recipients:
            person_message, created = PersonMessage.objects.get_or_create(
                person=person,
                message=self,
            )

            if created or resend:
                person_message.actually_send(delay)
                bodylen = len(person_message.body.text)
                delayfactor = ceil(bodylen / 153)
                delay += DELAY_PER_MESSAGE_FRAGMENT_MILLIS * delayfactor

    def expire(self):
        assert self.expired_at is None, 're-expiring an expired message does not make sense'
        assert self.sent_at is not None, 'expiring an unsent message does not make sense'

        self.expired_at = datetime.now()
        self.save()

    def unexpire(self):
        assert self.expired_at is not None, 'cannot un-expire a non-expired message'

        self.expired_at = None
        self.save()

        # Send to those that have been added to recipients while the message was expired
        self.send()

    @classmethod
    def send_messages(cls, event, app_label, person):
        for message in Message.objects.filter(
            recipient__app_label=app_label,
            recipient__event=event,
            recipient__group__in=person.user.groups.all(),
            sent_at__isnull=False,
            expired_at__isnull=True,
        ):
            message.send(recipients=[person,], resend=False)

    @property
    def event(self):
        return self.recipient.event

    @property
    def app_label(self):
        return self.recipient.app_label

    @property
    def app_event_meta(self):
        return self.event.app_event_meta(self.app_label)

    def __unicode__(self):
        return Template(self.subject_template).render(Context(dict(event=self.event)))

    class Meta:
        verbose_name = u'viesti'
        verbose_name_plural = u'viestit'


class DedupMixin(object):
    @classmethod
    def get_or_create(cls, text):
        the_hash = sha1(text.encode('UTF-8')).hexdigest()

        try:
            return cls.objects.get_or_create(
                digest=the_hash,
                defaults=dict(
                    text=text,
                )
            )
        except cls.MultipleObjectsReturned:
            logger.warn('Multiple %s returned for hash %s', cls.__name__, the_hash)
            return cls.objects.filter(digest=the_hash, text=text).first(), False


class PersonMessageSubject(models.Model, DedupMixin):
    digest = models.CharField(max_length=63, db_index=True)
    text = models.CharField(max_length=255)


class PersonMessageBody(models.Model, DedupMixin):
    digest = models.CharField(max_length=63, db_index=True)
    text = models.TextField()


class PersonMessage(models.Model):
    message = models.ForeignKey(Message)
    person = models.ForeignKey('core.Person')

    # dedup
    subject = models.ForeignKey(PersonMessageSubject)
    body = models.ForeignKey(PersonMessageBody)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.subject, unused = PersonMessageSubject.get_or_create(self.render_message(self.message.subject_template))
        self.body, unused = PersonMessageBody.get_or_create(self.render_message(self.message.body_template))

        return super(PersonMessage, self).save(*args, **kwargs)

    @property
    def message_vars(self):
        if not hasattr(self, '_message_vars'):
            self._message_vars = dict(
                event=self.message.event,
                person=self.person,
            )

            # TODO need a way to make app-specific vars in the apps themselves
            if 'labour' in settings.INSTALLED_APPS:
                from labour.models import Signup

                try:
                    signup = Signup.objects.get(event=self.message.event, person=self.person)
                except Signup.DoesNotExist:
                    signup = None

                self._message_vars.update(signup=signup)

        return self._message_vars

    def render_message(self, template):
        return Template(template).render(Context(self.message_vars))

    def actually_send(self, delay=0):
        if self.message.channel == 'email':
            self._actually_send_email()
        elif self.message.channel == 'sms':
            self._actually_send_sms(delay)
        else:
            raise NotImplementedError(self.message.channel)

    def _actually_send_email(self):
        from django.core.mail import EmailMessage

        msgbcc = []
        meta = self.message.app_event_meta

        if meta.monitor_email:
            msgbcc.append(meta.monitor_email)

        if settings.DEBUG:
            print self.body.text

        EmailMessage(
            subject=self.subject.text,
            body=self.body.text,
            from_email=meta.cloaked_contact_email,
            to=(self.person.name_and_email,),
            bcc=msgbcc
        ).send(fail_silently=True)

    def _actually_send_sms(self, delay=0):
        from sms.models import SMSMessageOut, SMSEventMeta
        try:
            event = SMSEventMeta.objects.get(event=self.message.event, sms_enabled=True)
        except SMSEventMeta.DoesNotExist:
            pass
        else:
            if 'background_tasks' in settings.INSTALLED_APPS:
                from sms.tasks import message_send
                sendtime = timezone.now() + timedelta(milliseconds=delay)
                sending = SMSMessageOut(message=self.body.text, to=self.person.phone, event=event)
                sending.save()
                message_send.apply_async(args=[sending.pk], eta=sendtime)
            else:
                SMSMessageOut.send(message=self.body.text, to=self.person.phone, event=event)
