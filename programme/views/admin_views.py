# encoding: utf-8

from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods, require_GET

from core.utils import initialize_form, url

from ..models import Programme
from ..helpers import programme_admin_required
from ..forms import ProgrammeForm, ProgrammeAdminForm, ProgrammeExtraForm


@programme_admin_required
def programme_admin_view(request, vars, event):
    programmes = Programme.objects.filter(category__event=event)

    vars.update(
        programmes=programmes
    )

    return render(request, 'programme_admin_view.jade', vars)


@programme_admin_required
@require_http_methods(['GET', 'POST'])
def programme_admin_detail_view(request, vars, event, programme_id=None):
    if programme_id:
        programme = get_object_or_404(Programme, category__event=event, pk=int(programme_id))
    else:
        programme = Programme()

    programme_form = initialize_form(ProgrammeForm, request,
        instance=programme,
        prefix='programme_basic',
    )
    programme_admin_form = initialize_form(ProgrammeAdminForm, request,
        instance=programme,
        prefix='programme_admin',
        event=event,
    )

    vars.update(
        programme=programme,
        programme_form=programme_form,
        programme_admin_form=programme_admin_form,
    )

    forms = [programme_form, programme_admin_form]

    if programme.pk:
        programme_extra_form = initialize_form(ProgrammeExtraForm, request,
            instance=programme,
            prefix='programme_extra',
            self_service=False,
        )
        vars.update(
            programme_extra_form=programme_extra_form
        )

        forms.append(programme_extra_form)

    if request.method == 'POST':
        if 'save' in request.POST:
            if all(form.is_valid() for form in forms):
                programme_form.save(commit=False)
                programme_admin_form.save(commit=False)

                if programme.pk:
                    programme_extra_form.save(commit=False)

                programme.save()
                messages.success(request, u'Ohjelmanumeron tiedot tallennettiin.')
                return redirect('programme_admin_detail_view', event.slug, programme.pk)
            else:
                messages.error(request, u'Ole hyvä ja tarkista lomake.')

        elif 'delete' in request.POST:
            programme.delete()
            messages.success(request, u'Ohjelmanumero poistettiin.')
            return redirect('programme_admin_view', event.slug)

        else:
            messages.error(request, u'Tunnistamaton pyyntö')

    return render(request, 'programme_admin_detail_view.jade', vars)


@programme_admin_required
@require_GET
def programme_admin_timetable_view(request, vars, event):
    from .public_views import actual_timetable_view

    return actual_timetable_view(
        request,
        event,
        internal_programmes=True,
        template='programme_admin_timetable_view.jade',
        vars=vars,
    )


def programme_admin_menu_items(request, event):
    timetable_url = url('programme_admin_timetable_view', event.slug)
    timetable_active = request.path == timetable_url
    timetable_text = u'Ohjelmakartan esikatselu'

    index_url = url('programme_admin_view', event.slug)
    index_active = request.path.startswith(index_url) and not timetable_active # XXX
    index_text = u'Ohjelmaluettelo'

    return [
        (index_active, index_url, index_text),
        (timetable_active, timetable_url, timetable_text),
    ]