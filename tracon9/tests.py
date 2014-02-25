# encoding: utf-8

from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.test import TestCase

from core.models import Event
from tickets.models import Product, Order, OrderProduct
from lippukala.models import Code, Order as LippukalaOrder
from lippukala.printing import OrderPrinter
from tracon9.lippukala_integration import Queue


def _create_order(num_tickets=2):
    call_command('setup_core', test=True)
    call_command('setup_labour_common_qualifications', test=True)
    call_command('setup_tracon9', test=True)

    event = Event.objects.get(name='Tracon 9')
    product = Product.objects.get(event=event, name__icontains='viikonlop', electronic_ticket=True)
    order, created = Order.get_or_create_dummy(event=event)
    OrderProduct.objects.get_or_create(order=order, product=product, defaults=dict(count=num_tickets))

    return order


class Tracon9LippukalaTestCase(TestCase):
    def test_manual_code_creation(self):
        if 'lippukala' not in settings.INSTALLED_APPS:
            print 'Test disabled due to lippukala not being installed'
            return

        num_tickets = 2

        order = _create_order(num_tickets)
        product = order.order_product_set.get().product

        lippukala_order = LippukalaOrder.objects.create(
            address_text=order.formatted_address,
            free_text=u"Tervetuloa Traconiin!",
            reference_number=order.reference_number,
        )

        codes = [Code.objects.create(
            order=lippukala_order,
            prefix=order.lippukala_prefix,
            product_text=product.name,
        ) for i in xrange(num_tickets)]

        for code in codes:
            print code.full_code, code.literate_code
            assert code.full_code.startswith(Queue.TWO_WEEKEND_TICKETS)
            assert code.literate_code.startswith(settings.LIPPUKALA_PREFIXES[Queue.TWO_WEEKEND_TICKETS])

        printer = OrderPrinter()
        printer.process_order(lippukala_order)

        with open(settings.MKPATH('tmp', 'temp.pdf'), 'wq') as output_file:
            output_file.write(printer.finish())

    def test_automatic_code_creation(self):
        if 'lippukala' not in settings.INSTALLED_APPS:
            print 'Test disabled due to lippukala not being installed'
            return

        call_command('setup_core', test=True)
        call_command('setup_labour_common_qualifications', test=True)
        call_command('setup_tracon9', test=True)

        num_tickets = 3

        order = _create_order(num_tickets)
        order.confirm_payment()

        assert len(mail.outbox) == 1

        msg = mail.outbox[0]

        assert len(msg.attachments) == 1