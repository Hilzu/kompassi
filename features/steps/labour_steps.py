from behave import given, when, then

from labour.models import LabourEventMeta, Signup


@given(u'there is an event that is accepting applications')
def given_event_accepting_applications(context):
    context.labour_event_meta, unused = LabourEventMeta.get_or_create_dummy()
    context.event = context.labour_event_meta.event


@when(u'I sign up for the event')
@given(u'I am signed up to the event')
def event_sign_up(context):
    context.signup, unused = Signup.get_or_create_dummy()
    context.signup.apply_state()


@when(u'the workforce manager approves my application')
@given(u'my application has been accepted')
def accept_the_application(context):
    old_state = context.signup.state

    context.signup.state = 'accepted'
    context.signup.save()

    context.signup.apply_state()


@when(u'the workforce manager assigns me to shifts')
def step_impl(context):
    old_state = context.signup.state

    context.signup.xxx_interim_shifts = "VUOROT"
    context.signup.state = 'finished'
    context.signup.save()
    
    context.signup.apply_state()


@given(u'my application has been rejected')
def step_impl(context):
    old_state = context.signup.state

    context.signup.state = 'rejected'
    context.signup.save()
    
    context.signup.apply_state()