# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateResponseMixin

from rules.contrib.views import PermissionRequiredMixin

from localhub.communities.views import CommunityRequiredMixin
from localhub.views import SuccessActionView

from ..models import Answer, Poll


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
