# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

# Third Party Libraries
from turbo_response import TurboFrame, redirect_303

# Localhub
from localhub.activities.views.generic import (
    get_activity_or_404,
    get_activity_queryset,
    process_activity_create_form,
    process_activity_update_form,
    render_activity_create_form,
    render_activity_detail,
    render_activity_list,
    render_activity_update_form,
)
from localhub.communities.decorators import community_required
from localhub.users.utils import has_perm_or_403

# Local
from .models import Answer, Poll

AnswersFormSet = inlineformset_factory(
    Poll,
    Answer,
    fields=("description",),
    extra=4,
    max_num=4,
    min_num=2,
    labels={"description": ""},
)


@community_required
def poll_list_view(request, model, template_name):
    qs = get_activity_queryset(
        request, model, with_common_annotations=True
    ).with_answers()
    return render_activity_list(request, qs, template_name)


@community_required
@login_required
@require_POST
def answer_vote_view(request, pk):

    answer = get_object_or_404(
        Answer.objects.filter(poll__community=request.community).select_related(
            "poll", "poll__community"
        ),
        pk=pk,
    )

    has_perm_or_403(request.user, "polls.vote", answer.poll)

    has_voted = False

    for voted in Answer.objects.filter(voters=request.user, poll=answer.poll):
        voted.voters.remove(request.user)
        has_voted = True

    answer.voters.add(request.user)

    # send notification only the first time someone votes

    if not has_voted:
        answer.poll.notify_on_vote(request.user)

    # reload to get with updated answers
    poll = get_object_or_404(Poll.objects.with_answers(), pk=answer.poll_id)

    return (
        TurboFrame(f"poll-answers-{poll.id}")
        .template(
            "polls/includes/answers.html", {"object": poll, "object_type": "poll",},
        )
        .response(request)
    )


@community_required
@login_required
def poll_create_view(request, model, form_class, template_name, is_private=False):

    has_perm_or_403(request.user, "activities.create_activity", request.community)

    if request.method == "POST":
        formset = AnswersFormSet(request.POST)
    else:
        formset = AnswersFormSet()

    obj, form, success = process_activity_create_form(
        request, model, form_class, is_private=is_private
    )

    if success and formset.is_valid():
        formset.instance = obj
        formset.save()
        return redirect_303(obj)

    return render_activity_create_form(
        request,
        model,
        form,
        template_name,
        is_private=is_private,
        extra_context={"answers_formset": formset},
    )


@community_required
@login_required
def poll_update_view(request, pk, model, form_class, template_name):

    obj = get_activity_or_404(
        request, model, pk, permission="activities.change_activity"
    )

    if request.method == "POST":
        formset = AnswersFormSet(request.POST, instance=obj)
    else:
        formset = AnswersFormSet(instance=obj)

    obj, form, success = process_activity_update_form(request, form_class, instance=obj)

    if success and formset.is_valid():
        formset.save()
        return redirect_303(obj)

    return render_activity_update_form(
        request, obj, form, template_name, extra_context={"answers_formset": formset},
    )


@community_required
def poll_detail_view(request, pk, model, template_name, slug=None):
    obj = get_object_or_404(
        get_activity_queryset(
            request, model, with_common_annotations=True
        ).with_answers(),
        pk=pk,
    )
    return render_activity_detail(request, obj, template_name)
