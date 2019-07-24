# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Set, Union
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.validators import RegexValidator, URLValidator
from django.db import models
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _


from model_utils import Choices
from model_utils.models import TimeStampedModel

from localhub.core.markdown.fields import MarkdownField
from localhub.core.markdown.utils import extract_hashtags

DOMAIN_VALIDATOR = RegexValidator(
    regex=URLValidator.host_re, message=_("This is not a valid domain")
)


class RequestCommunity:
    """
    This works in a similar way to Django auth AnonymousUser, if
    no community present. It provides ducktyping so we don't have to check
    for None everywhere. Wraps HttpRequest/Site.
    """

    id = None
    pk = None
    public = False
    active = False

    def __init__(self, request: HttpRequest):
        self.request = request
        self.site = get_current_site(request)
        self.name = self.site.name
        self.domain = self.site.domain

    def get_absolute_url(self) -> str:
        return self.request.full_path

    def user_has_role(self, user: settings.AUTH_USER_MODEL, role: str) -> bool:
        return False


class CommunityManager(models.Manager):
    use_in_migrations = True

    def get_current(
        self, request: HttpRequest
    ) -> Union["Community", "RequestCommunity"]:
        """
        Returns current community matching request domain if active.
        """
        try:
            return self.get(
                active=True, domain__iexact=request.get_host().split(":")[0]
            )
        except self.model.DoesNotExist:
            return RequestCommunity(request)


class Community(TimeStampedModel):
    domain = models.CharField(
        unique=True, max_length=100, validators=[DOMAIN_VALIDATOR]
    )

    name = models.CharField(max_length=255)
    description = MarkdownField(blank=True)
    terms = MarkdownField(
        blank=True,
        help_text=_(
            "Terms and conditions, code of conduct and other membership terms."
        ),
    )

    content_warning_tags = models.TextField(
        blank=True,
        default="#nsfw",
        help_text=_(
            "Any posts containing these tags in their description will be automatically hidden by default"  # noqa
        ),
    )

    email_domain = models.CharField(
        null=True,
        blank=True,
        max_length=100,
        validators=[DOMAIN_VALIDATOR],
        help_text=_(
            "Will add domain to notification emails from this site, e.g. "
            "notifications@this-domain.com. If left empty will use the site "
            "domain by default."
        ),
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Membership",
        related_name="communities",
    )

    public = models.BooleanField(
        default=True,
        help_text=_(
            "This community is open to the world. "
            "Non-members can view all published content."
        ),
    )

    active = models.BooleanField(
        default=True, help_text=_("This community is currently live.")
    )

    objects = CommunityManager()

    class Meta:
        verbose_name_plural = _("Communities")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return f"http://{self.domain}"

    def get_email_domain(self) -> str:
        """
        Returns email domain if available, else the community domain
        """
        return self.email_domain or self.domain

    def get_content_warning_tags(self) -> Set[str]:
        return extract_hashtags(self.content_warning_tags)

    def resolve_url(self, url: str) -> str:
        """
        Prepends the community domain to create a complete URL string
        """
        return urljoin(self.get_absolute_url(), url)

    def resolve_email(self, local_part: str) -> str:
        """
        Appends the email domain to create a full email address
        """
        return f"{local_part}@{self.get_email_domain()}"

    def get_members_by_role(self, role: str) -> models.QuerySet:
        return self.members.filter(membership__role=role)

    def get_members(self) -> models.QuerySet:
        return self.get_members_by_role(Membership.ROLES.member)

    def get_moderators(self) -> models.QuerySet:
        return self.get_members_by_role(Membership.ROLES.moderator)

    def get_admins(self) -> models.QuerySet:
        return self.get_members_by_role(Membership.ROLES.admin)

    def user_has_role(self, user: settings.AUTH_USER_MODEL, role: str) -> bool:
        if user.is_anonymous:
            return False
        return user.has_role(self, role)


class Membership(TimeStampedModel):
    ROLES = Choices(
        ("member", _("Member")),
        ("moderator", _("Moderator")),
        ("admin", _("Admin")),
    )

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    role = models.CharField(
        choices=ROLES, max_length=9, default=ROLES.member, db_index=True
    )
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["member", "community"], name="unique_membership"
            )
        ]
        indexes = [models.Index(fields=["member", "community", "active"])]

    def __str__(self) -> str:
        return self.get_role_display()
