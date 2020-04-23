# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.forms import inlineformset_factory
from django.utils.functional import cached_property

from localhub.activities.views.create_update import (
    ActivityCreateView,
    ActivityUpdateView,
)

from ..models import Answer, Poll


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
