# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Dict, List, Optional, Sequence

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from model_utils import Choices

from sorl.thumbnail import ImageField

from taggit.models import Tag

from localhub.communities.models import Community, Membership
from localhub.core.fields import ChoiceArrayField
from localhub.core.markdown.fields import MarkdownField
from localhub.notifications.models import Notification


class UserQuerySet(models.QuerySet):
    use_in_migrations = True

    def for_email(self, email: str) -> models.QuerySet:
        """
        Returns all users with primary or additional emails matching
        this email (case insensitive).
        """
        return self.filter(
            models.Q(emailaddress__email__iexact=email)
            | models.Q(email__iexact=email)
        )

    def with_is_following(
        self, follower: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        return self.annotate(
            is_following=models.Exists(
                follower.following.filter(pk__in=models.OuterRef("id"))
            )
        )

    def with_is_blocked(
        self, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        return self.annotate(
            is_blocked=models.Exists(
                user.blocked.filter(pk__in=models.OuterRef("id"))
            )
        )

    def matches_usernames(self, names=Sequence[str]) -> models.QuerySet:
        """
        Returns any users matching username (case insensitive).
        """
        if not names:
            return self.none()
        return self.filter(username__iregex=r"^(%s)+" % "|".join(names))

    def active(self, community: Community) -> models.QuerySet:
        """
        Returns only users which are a) active and b) have active
        membership with given community.
        """

        return self.filter(
            # test with more than 1 community
            membership__community=community,
            membership__active=True,
            is_active=True,
        )


class UserManager(BaseUserManager):
    def get_queryset(self) -> models.QuerySet:
        return UserQuerySet(self.model, using=self._db)

    def with_is_following(
        self, follower: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        return self.get_queryset().with_is_following(follower)

    def with_is_blocked(
        self, follower: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        return self.get_queryset().with_is_blocked(follower)

    def active(self, community: Community) -> models.QuerySet:
        return self.get_queryset().active(community)

    def for_email(self, email: str) -> models.QuerySet:
        return self.get_queryset().for_email(email)

    def matches_usernames(self, names=Sequence[str]) -> models.QuerySet:
        return self.get_queryset().matches_usernames(names)

    def create_user(
        self,
        username: str,
        email: str,
        password: Optional[str] = None,
        **kwargs
    ) -> settings.AUTH_USER_MODEL:
        user = self.model(
            username=username, email=self.normalize_email(email), **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, username: str, email: str, password: str, **kwargs
    ) -> settings.AUTH_USER_MODEL:
        return self.create_user(
            username,
            email,
            password,
            is_staff=True,
            is_superuser=True,
            **kwargs
        )


class User(AbstractUser):

    HOME_PAGE_FILTERS = Choices(
        ("users", _("Posts from people I'm following")),
        ("tags", _("Posts containing tags I'm following")),
    )

    EMAIL_PREFERENCES = Choices(
        ("new_message", _("I receive a direct message")),
        ("new_follower", _("Someone starts following me")),
        ("new_comment", _("Someone comments on my post")),
        ("reshare", _("Someone has reshared my post")),
        ("mention", _("I am @mentioned in a post or comment")),
        ("moderator_delete", _("A moderator deletes my post or comment")),
        ("moderator_edit", _("A moderator edits my post or comment")),
        ("like", _("Someone likes my post or comment")),
        ("new_followed_user_post", _("Someone I'm following creates a post")),
        (
            "new_followed_tag_post",
            _("A post is created containing tags I'm following"),
        ),
        ("flag", _("A user has flagged a comment or post (moderators only)")),
        (
            "moderator_review_request",
            _(
                "A user has a new comment or post for you to "
                "review (moderators only)"
            ),
        ),
    )

    name = models.CharField(_("Full name"), blank=True, max_length=255)
    bio = MarkdownField(blank=True)
    avatar = ImageField(upload_to="avatars", null=True, blank=True)

    home_page_filters = ChoiceArrayField(
        models.CharField(max_length=12, choices=HOME_PAGE_FILTERS),
        default=list,
        blank=True,
    )

    show_sensitive_content = models.BooleanField(default=False)

    email_preferences = ChoiceArrayField(
        models.CharField(max_length=12, choices=EMAIL_PREFERENCES),
        default=list,
        blank=True,
    )

    following = models.ManyToManyField(
        "self", related_name="followers", blank=True, symmetrical=False
    )

    blocked = models.ManyToManyField(
        "self", related_name="blockers", blank=True, symmetrical=False
    )

    following_tags = models.ManyToManyField(Tag, related_name="+", blank=True)

    blocked_tags = models.ManyToManyField(Tag, related_name="+", blank=True)

    objects = UserManager()

    def get_absolute_url(self) -> str:
        return reverse("users:activities", args=[self.username])

    def has_email_pref(self, pref: str) -> bool:
        return (
            pref in self.email_preferences if self.email_preferences else False
        )

    def has_role(self, community: Community, role: str) -> bool:
        """
        Checks if user has given role in the community, if any. Result
        is cached.
        """
        return self.community_roles_cache.get(community.id, None) == role

    def get_unread_notification_count(self, community: Community) -> int:
        """Gets number of unread notifications. Result is cached."""
        return self.unread_notification_counts_cache.get(community.id, 0)

    def get_unread_message_count(self, community: Community) -> int:
        """Gets number of unread direct messages. Result is cached."""
        return self.unread_message_counts_cache.get(community.id, 0)

    @cached_property
    def unread_notification_counts_cache(self) -> Dict[int, int]:
        return dict(
            Community.objects.annotate(
                num_notifications=models.Count(
                    "notification",
                    filter=models.Q(
                        notification__is_read=False,
                        notification__recipient=self,
                    ),
                )
            ).values_list("id", "num_notifications")
        )

    @cached_property
    def unread_message_counts_cache(self) -> Dict[int, int]:
        return dict(
            Community.objects.annotate(
                num_messages=models.Count(
                    "message__messagerecipient",
                    filter=models.Q(
                        message__messagerecipient__read__isnull=True,
                        message__messagerecipient__recipient=self,
                    ),
                )
            ).values_list("id", "num_messages")
        )

    @cached_property
    def community_roles_cache(self) -> Dict[int, str]:
        return dict(
            Membership.objects.filter(active=True, member=self).values_list(
                "community", "role"
            )
        )

    def notify(
        self, recipient: settings.AUTH_USER_MODEL, community: Community
    ) -> List[Notification]:
        """
        Sends notification to provided recipients
        """

        notifications = [
            Notification.objects.create(
                content_object=recipient,
                recipient=recipient,
                actor=self,
                community=community,
                verb="follow",
            )
        ]

        return notifications
