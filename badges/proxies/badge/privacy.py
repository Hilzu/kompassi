# encoding: utf-8

from __future__ import unicode_literals


class BadgePrivacyAdapter(object):
    """
    Our CSV infrastructure has a nasty reversion of control: it getattrs us for the fields instead of
    asking us to supply whatever field values we want.

    So first_name in Badge can't be anything else that the actual database-backed property.

    Let's put an adapter in the middle that is responsible for monitoring the is_*_visible policy.

    Note that the real_name_must_be_visible/CONDB-423 policy is implemented before this point. This lets
    us print nameless badges if we *really* want to, for example for actual stalker cases.

    Not really a proxy model.
    """

    __slots__ = ['badge']

    def __init__(self, badge):
        self.badge = badge

    def __unicode__(self):
        return self.badge.__unicode__()

    @property
    def first_name(self):
        return self.badge.first_name.strip() if self.badge.is_first_name_visible else u''

    @property
    def surname(self):
        return self.badge.surname.strip() if self.badge.is_surname_visible else u''

    @property
    def nick(self):
        return self.badge.nick.strip() if self.badge.is_nick_visible else u''

    @property
    def nick_or_first_name(self):
        if self.badge.is_nick_visible:
            # JAPSU <- this
            # Santtu Pajukanta
            # Chief Technology Officer
            return self.badge.nick
        elif self.badge.is_first_name_visible:
            # SANTTU <- this
            # Pajukanta
            # Chief Technology Officer
            return self.badge.first_name
        else:
            return ""

    @property
    def surname_or_full_name(self):
        if self.badge.is_nick_visible:
            # JAPSU
            # Santtu Pajukanta <- this
            # Chief Technology Officer
            if self.badge.is_surname_visible:
                if self.badge.is_first_name_visible:
                    return "{first_name} {surname}".format(
                        first_name=self.badge.first_name,
                        surname=self.badge.surname,
                    )
                else:
                    return self.badge.surname
            else:
                return ""
        else:
            # SANTTU
            # Pajukanta <- this
            # Chief Technology Officer
            if self.badge.is_surname_visible:
                return self.badge.surname
            else:
                return ""