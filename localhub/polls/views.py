# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.shortcuts import redirect
from django.utils.translation import gettext as _


from vanilla import GenericModelView

from rules.contrib.views import PermissionRequiredMixin

from localhub.activities.views.generic import (
    ActivityCreateView,
    ActivityDetailView,
    ActivityListView,
    ActivityUpdateView,
)
from localhub.communities.views import CommunityRequiredMixin
from localhub.polls.models import Poll, Answer

AnswersFormSet = inlineformset_factory(
    Poll, Answer, fields=("description",), extra=3, max_num=4
)


class PollQuerySetMixin:
    def get_queryset(self):
        return super().get_queryset().with_voting_counts()


class PollCreateView(ActivityCreateView):
    model = Poll

    def get(self, request):
        self.answers_formset = AnswersFormSet()
        return super().get(request)

    def form_invalid(self, form, answers_formset=None):
        self.answers_formset = answers_formset or AnswersFormSet(
            self.request.POST
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        answers_formset = AnswersFormSet(self.request.POST)
        if not answers_formset.is_valid():
            return self.form_invalid(form, answers_formset)
        response = super().form_valid(form)
        answers_formset.instance = self.object
        answers_formset.save()
        return response

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["answers_formset"] = self.answers_formset
        return data


class PollUpdateView(ActivityUpdateView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.answers_formset = AnswersFormSet(instance=self.object)
        form = self.get_form(instance=self.object)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def form_invalid(self, form, answers_formset=None):
        self.answers_formset = answers_formset or AnswersFormSet(
            self.request.POST, instance=self.object
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        answers_formset = AnswersFormSet(
            self.request.POST, instance=self.object
        )
        if not answers_formset.is_valid():
            return self.form_invalid(form, answers_formset)
        response = super().form_valid(form)
        answers_formset.save()
        return response

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["answers_formset"] = self.answers_formset
        return data


class PollDetailView(PollQuerySetMixin, ActivityDetailView):
    ...


class PollListView(PollQuerySetMixin, ActivityListView):
    ...


class AnswerVoteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CommunityRequiredMixin,
    GenericModelView,
):

    permission_required = "polls.vote"

    def get_permission_object(self):
        return self.get_object().poll

    def get_queryset(self):
        return Answer.objects.filter(poll__community=self.request.community)

    def post(self, request, *args, **kwargs):
        answer = self.get_object()
        for voted in Answer.objects.filter(
            voters=self.request.user, poll=answer.poll
        ):
            voted.voters.remove(self.request.user)
        answer.voters.add(self.request.user)
        messages.success(self.request, _("Thanks for voting!"))
        return redirect(answer.poll)


answer_vote_view = AnswerVoteView.as_view()
