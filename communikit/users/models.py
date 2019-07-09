# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Optional, Sequence

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from sorl.thumbnail import ImageField


from communikit.communities.models import Community
from communikit.core.markdown.fields import MarkdownField
from communikit.subscriptions.models import (
    Subscription,
    SubscriptionAnnotationsQuerySetMixin,
)


class UserManager(SubscriptionAnnotationsQuerySetMixin, BaseUserManager):
    use_in_migrations = True

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

    def for_email(self, email: str) -> models.QuerySet:
        return self.filter(
            models.Q(emailaddress__email__iexact=email)
            | models.Q(email__iexact=email)
        )

    def matches_usernames(self, names=Sequence[str]) -> models.QuerySet:
        # sanity check
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


class User(AbstractUser):
    name = models.CharField(_("Full name of user"), blank=True, max_length=255)
    bio = MarkdownField(blank=True)
    avatar = ImageField(upload_to="avatars", null=True, blank=True)

    subscriptions = GenericRelation(Subscription, related_query_name="user")

    objects = UserManager()

    def get_absolute_url(self) -> str:
        return reverse("users:detail", args=[self.username])
