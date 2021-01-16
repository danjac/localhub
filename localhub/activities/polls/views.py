# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin

# Third Party Libraries
from rules.contrib.views import PermissionRequiredMixin
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
from localhub.communities.mixins import CommunityRequiredMixin
from localhub.users.utils import has_perm_or_403

# Local
from .models import Answer, Poll


@community_required
def poll_list_view(request, model, template_name):
    qs = get_activity_queryset(
        request, model, with_common_annotations=True
    ).with_answers()
    return render_activity_list(request, qs, template_name)


class AnswerVoteView(
    TemplateResponseMixin,
    PermissionRequiredMixin,
    CommunityRequiredMixin,
    SingleObjectMixin,
    View,
):
    """
    Returns HTTP fragment in AJAX response when user has voted.
    """

    permission_required = "polls.vote"
    template_name = "polls/includes/answers.html"

    @cached_property
    def object(self):
        return self.get_object()

    def get_permission_object(self):
        return self.object.poll

    def get_queryset(self):
        return Answer.objects.filter(
            poll__community=self.request.community
        ).select_related("poll", "poll__community")

    def post(self, request, *args, **kwargs):
        has_voted = False
        for voted in Answer.objects.filter(
            voters=self.request.user, poll=self.object.poll
        ):
            voted.voters.remove(self.request.user)
            has_voted = True

        self.object.voters.add(self.request.user)

        # send notification only the first time someone votes
        if not has_voted:
            self.object.poll.notify_on_vote(self.request.user)

        poll = get_object_or_404(Poll.objects.with_answers(), pk=self.object.poll_id)

        context = {
            "object": poll,
            "object_type": "poll",
        }

        return (
            TurboFrame(f"poll-answers-{poll.id}")
            .template("polls/includes/answers.html", context)
            .response(request)
        )


answer_vote_view = AnswerVoteView.as_view()


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
@login_required
def poll_create_view(request, model, form_class, template_name, is_private=False):

    has_perm_or_403(request.user, "activities.create_activity", request.community)

    if request.method == "POST":
        form = form_class(request.POST)
        formset = AnswersFormSet(request.POST)
    else:
        form = form_class()
        formset = AnswersFormSet()

    obj, ok = process_activity_create_form(request, model, form, is_private=is_private)

    if ok and formset.is_valid():
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
        form = form_class(request.POST, instance=obj)
        formset = AnswersFormSet(request.POST, instance=obj)
    else:
        form = form_class(instance=obj)
        formset = AnswersFormSet(instance=obj)

    obj, ok = process_activity_update_form(request, obj, form)

    if ok and formset.is_valid():
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
