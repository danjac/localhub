# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Sequence

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    def matches_usernames(self, names=Sequence[str]) -> models.QuerySet:
        # sanity check
        if not names:
            return self.none()
        return self.filter(username__iregex=r"^(%s)+" % "|".join(names))


class User(AbstractUser):
    name = models.CharField(_("Full name of user"), blank=True, max_length=255)

    objects = UserManager()

    def get_profile_url(self) -> str:
        """
        Link to (public) profile content page
        """
        return reverse("activities:profile", args=[self.username])
