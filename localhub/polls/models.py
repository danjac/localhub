# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from localhub.activities.models import Activity, ActivityQuerySet
from localhub.db.search import SearchIndexer


class PollQuerySet(ActivityQuerySet):
    def with_answers(self):
        return self.prefetch_related(
            models.Prefetch(
                "answers",
                queryset=Answer.objects.annotate(
                    num_votes=models.Count("voters", distinct=True)
                ).order_by("id"),
            )
        )

    def for_activity_stream(self, user, community):
        return super().for_activity_stream(user, community).with_answers()


class Poll(Activity):

    search_indexer = SearchIndexer(("A", "title"), ("B", "description"))

    objects = PollQuerySet.as_manager()

    def __str__(self):
        return self.title or _("Poll")

    @cached_property
    def total_num_votes(self):
        """
        Returns number of votes. Use in conjunction with with_answers()
        method in queryset!
        """
        return sum([a.num_votes for a in self.answers.all()])

    def notify_on_vote(self, voter):
        """
        Sends a notification when someone has voted. Ignore if you
        vote on your own poll.
        """
        if voter == self.owner:
            return []
        return [self.make_notification(self.owner, "vote", voter)]

    def get_notification_header(self, notification):
        if notification.verb == "vote":
            return "Someone has voted on your poll"
        return super().get_notification_header(notification)

    def get_notification_plain_email_template(self, notification):
        if notification.verb == "vote":
            return "polls/emails/notifications/vote.txt"
        return super().get_notification_plain_email_template(notification)

    def get_notification_html_email_template(self, notification):
        if notification.verb == "vote":
            return "polls/emails/notifications/vote.html"
        return super().get_notification_html_email_template(notification)


class Answer(models.Model):
    poll = models.ForeignKey(Poll, related_name="answers", on_delete=models.CASCADE)
    description = models.CharField(max_length=180)
    voters = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return self.description
