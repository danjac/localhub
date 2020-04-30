# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateResponseMixin

from rules.contrib.views import PermissionRequiredMixin

from localhub.apps.activities.views.create_update import (
    ActivityCreateView,
    ActivityUpdateView,
)
from localhub.apps.activities.views.list_detail import (
    ActivityDetailView,
    ActivityListView,
)
from localhub.apps.communities.views import CommunityRequiredMixin
from localhub.common.views import SuccessActionView

from .models import Answer, Poll


class PollQuerySetMixin:
    def get_queryset(self):
        return super().get_queryset().with_answers()


class AnswerVoteView(
    TemplateResponseMixin,
    PermissionRequiredMixin,
    CommunityRequiredMixin,
    SuccessActionView,
):
    """
    Returns HTTP fragment in AJAX response when user has voted.
    """

    permission_required = "polls.vote"
    template_name = "polls/includes/answers.html"

    success_message = _("Thanks for voting!")

    def get_permission_object(self):
        return self.object.poll

    def get_queryset(self):
        return Answer.objects.filter(
            poll__community=self.request.community
        ).select_related("poll", "poll__community")

    def get_success_response(self):
        # reload poll with revised answers and total count
        # and return HTML fragment
        return self.render_to_response(
            {
                "object": get_object_or_404(
                    Poll.objects.with_answers(), pk=self.object.poll_id
                ),
                "object_type": "poll",
            }
        )

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

        return self.success_response()


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
