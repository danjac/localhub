# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin

# Third Party Libraries
from rules.contrib.views import PermissionRequiredMixin
from turbo_response import TurboFrame

# Localhub
from localhub.activities.views.generic import (
    ActivityCreateView,
    ActivityDetailView,
    ActivityListView,
    ActivityUpdateView,
)
from localhub.communities.mixins import CommunityRequiredMixin

# Local
from .models import Answer, Poll


class PollQuerySetMixin:
    def get_queryset(self):
        return super().get_queryset().with_answers()


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


class AnswersFormSetMixin:
    AnswersFormSet = inlineformset_factory(
        Poll,
        Answer,
        fields=("description",),
        extra=4,
        max_num=4,
        min_num=2,
        labels={"description": ""},
    )

    @cached_property
    def answers_formset(self):
        instance = getattr(self, "object", None)
        if self.request.method == "POST":
            return self.AnswersFormSet(self.request.POST, instance=instance)
        return self.AnswersFormSet(instance=instance)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["answers_formset"] = self.answers_formset
        return data


class PollCreateView(AnswersFormSetMixin, ActivityCreateView):
    model = Poll

    def form_valid(self, form):
        if not self.answers_formset.is_valid():
            return self.form_invalid(form)
        response = super().form_valid(form)
        self.answers_formset.instance = self.object
        self.answers_formset.save()
        return response


class PollUpdateView(AnswersFormSetMixin, ActivityUpdateView):
    def form_valid(self, form):
        if not self.answers_formset.is_valid():
            return self.form_invalid(form)
        response = super().form_valid(form)
        self.answers_formset.save()
        return response


class PollDetailView(PollQuerySetMixin, ActivityDetailView):
    ...


class PollListView(PollQuerySetMixin, ActivityListView):
    ...
