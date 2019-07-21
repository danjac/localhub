# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Optional, Sequence

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from model_utils import Choices

from sorl.thumbnail import ImageField


from localhub.communities.models import Community
from localhub.core.fields import ChoiceArrayField
from localhub.core.markdown.fields import MarkdownField
from localhub.subscriptions.models import (
    Subscription,
    SubscriptionAnnotationsQuerySetMixin,
)


class UserQuerySet(SubscriptionAnnotationsQuerySetMixin, models.QuerySet):
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
    EMAIL_PREFERENCES = Choices(
        ("comments", _("Someone comments on my post")),
        ("deletes", _("A moderator deletes my post or comment")),
        ("edits", _("A moderator edits my post or comment")),
        ("follows", _("Someone I'm following creates a post")),
        ("likes", _("Someone likes my post or comment")),
        ("mentions", _("I am @mentioned in a post or comment")),
        ("messages", _("I receive a direct message")),
        ("tags", _("A post is created containing tags I'm following")),
        ("flags", _("Post or comment is flagged (MODERATORS ONLY)")),
        ("reviews", _("Content to be reviewed (MODERATORS ONLY)")),
    )

    name = models.CharField(_("Full name"), blank=True, max_length=255)
    bio = MarkdownField(blank=True)
    avatar = ImageField(upload_to="avatars", null=True, blank=True)

    email_preferences = ChoiceArrayField(
        models.CharField(max_length=12, choices=EMAIL_PREFERENCES),
        default=list,
        blank=True,
    )

    subscriptions = GenericRelation(Subscription, related_query_name="user")

    objects = UserManager()

    def get_absolute_url(self) -> str:
        return reverse("users:detail", args=[self.username])

    def has_email_pref(self, pref: str) -> bool:
        return pref in self.email_preferences or []
