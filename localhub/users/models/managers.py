# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.contrib.auth.models import BaseUserManager
from django.db import models

from localhub.communities.models import Membership
from localhub.db.search import SearchQuerySetMixin


class UserQuerySet(SearchQuerySetMixin, models.QuerySet):
    def for_email(self, email):
        """Returns users matching this email address, including both
        primary and secondary email addresses

        Args:
            email (str): email address

        Returns:
            QuerySet
        """
        return self.filter(
            models.Q(emailaddress__email__iexact=email) | models.Q(email__iexact=email)
        )

    def with_num_unread_messages(self, recipient, community):
        """Returns annotation of number of unread private messages sent by this user.

        Annotates "num_unread_messages" to QuerySet.

        Args:
            recipient (User): message recipient

        Returns:
            QuerySet
        """
        return self.annotate(
            num_unread_messages=models.Count(
                "sent_messages",
                filter=models.Q(
                    sent_messages__recipient=recipient,
                    sent_messages__community=community,
                    sent_messages__read__isnull=True,
                    sent_messages__sender_deleted__isnull=True,
                    sent_messages__recipient_deleted__isnull=True,
                ),
                distinct=True,
            )
        )

    def with_is_following(self, follower):
        """Annotates if user is a follower with attribute is_following.

        Args:
            follower (User)

        Returns:
            QuerySet
        """
        return self.annotate(
            is_following=models.Exists(
                follower.following.filter(pk=models.OuterRef("id"))
            )
        )

    def with_is_blocked(self, blocker):
        """Adds is_blocked annotation if in user's blocked list.

        Args:
            blocker (User)

        Returns:
            QuerySet
        """
        return self.annotate(
            is_blocked=models.Exists(blocker.blocked.filter(pk=models.OuterRef("id")))
        )

    def matches_usernames(self, names):
        """Returns users matching the (case insensitive) username.

        Args:
            names (list): list of usernames

        Returns:
            QuerySet
        """
        if not names:
            return self.none()
        return self.filter(username__iregex=r"^(%s)+" % "|".join(names))

    def for_community(self, community):
        """ Returns only users which are a) active and b) have active
        membership with given community.

        Args:
            community {Community}

        Returns:
            QuerySet
        """
        return self.filter(
            membership__community=community, membership__active=True, is_active=True,
        )

    def with_joined(self, community):
        """Adds "joined" datetime annotation.

        Args:
            community (Community)

        Returns:
            QuerySet
        """
        return self.annotate(
            joined=models.Subquery(
                Membership.objects.filter(
                    community=community, member=models.OuterRef("pk")
                ).values("created"),
                output_field=models.DateTimeField(),
            ),
        )

    def with_role(self, community):
        """Adds annotations "role", "joined" and "role_display" for users for this community.
        Use in conjunction with for_community.

        Args:
            community (Community)

        Returns:
            QuerySet
        """
        return self.annotate(
            role=models.Subquery(
                Membership.objects.filter(
                    community=community, member=models.OuterRef("pk")
                ).values("role"),
                output_field=models.CharField(),
            ),
            role_display=models.Case(
                *[
                    models.When(role=k, then=models.Value(str(v)))
                    for k, v in Membership.Role.choices
                ],
                default=models.Value(""),
                output_field=models.CharField(),
            ),
        )

    def exclude_blockers(self, user):
        """Exclude users blocking this user.

        Args:
            user (User)

        Returns:
            QuerySet
        """
        return self.exclude(blocked=user)

    def exclude_blocked(self, user):
        """Exclude users blocked by this user.

        Args:
            user (User)

        Returns:
            QuerySet
        """
        return self.exclude(blockers=user)

    def exclude_blocking(self, user):
        """Exclude users either blocked by this user, or blocking this user.

        Args:
            user (User)

        Returns:
            QuerySet
        """
        return self.exclude_blockers(user) & self.exclude_blocked(user)


class UserManager(BaseUserManager.from_queryset(UserQuerySet)):
    def create_user(self, username, email, password=None, **kwargs):
        user = self.model(
            username=username, email=self.normalize_email(email), **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **kwargs):
        return self.create_user(
            username, email, password, is_staff=True, is_superuser=True, **kwargs,
        )
