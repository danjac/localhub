# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from urllib.parse import urljoin

from django.conf import settings
from django.core.validators import RegexValidator, URLValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from model_utils.models import TimeStampedModel
from sorl.thumbnail import ImageField

from localhub.apps.hashtags.utils import extract_hashtags
from localhub.common.markdown.fields import MarkdownField

from .managers import CommunityManager, MembershipManager

DOMAIN_VALIDATOR = RegexValidator(
    regex=URLValidator.host_re, message=_("This is not a valid domain")
)


class Community(TimeStampedModel):
    domain = models.CharField(
        unique=True, max_length=100, validators=[DOMAIN_VALIDATOR]
    )

    name = models.CharField(max_length=255)

    logo = ImageField(upload_to="logo", null=True, blank=True)

    tagline = models.TextField(blank=True)

    intro = MarkdownField(blank=True)

    description = MarkdownField(blank=True)

    terms = MarkdownField(blank=True,)

    content_warning_tags = models.TextField(blank=True, default="#nsfw")

    email_domain = models.CharField(
        null=True, blank=True, max_length=100, validators=[DOMAIN_VALIDATOR],
    )

    google_tracking_id = models.CharField(null=True, blank=True, max_length=30)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Membership", related_name="communities",
    )

    active = models.BooleanField(default=True)

    public = models.BooleanField(default=True)

    allow_join_requests = models.BooleanField(default=True)

    blacklisted_email_domains = models.TextField(blank=True)

    blacklisted_email_addresses = models.TextField(blank=True)

    objects = CommunityManager()

    class Meta:
        verbose_name_plural = _("Communities")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        protocol = "https" if settings.SECURE_SSL_REDIRECT else "http"
        return f"{protocol}://{self.domain}"

    def get_email_domain(self):
        """
        Returns email domain if available, else the community domain
        """
        return (self.email_domain or self.domain).split(":")[0]

    def get_content_warning_tags(self):
        return extract_hashtags(self.content_warning_tags)

    def resolve_url(self, url):
        """
        Prepends the community domain to create a complete URL string
        """
        return urljoin(self.get_absolute_url(), url)

    def resolve_email(self, local_part):
        """
        Appends the email domain to create a full email address
        """
        return f"{local_part}@{self.get_email_domain()}"

    def get_members_by_role(self, *roles, active=True):
        qs = self.members.filter(membership__role__in=roles)
        if active:
            qs = qs.filter(membership__active=True, is_active=True)
        return qs

    def get_members(self, active=True):
        return self.get_members_by_role(
            Membership.Role.MEMBER,
            Membership.Role.MODERATOR,
            Membership.Role.ADMIN,
            active=active,
        )

    def get_moderators(self, active=True):
        return self.get_members_by_role(
            Membership.Role.MODERATOR, Membership.Role.ADMIN, active=active,
        )

    def get_admins(self, active=True):
        return self.get_members_by_role(Membership.Role.ADMIN, active=active)

    def is_email_blacklisted(self, email):
        """
        Checks if email address or domain is blacklisted by this community.
        """
        email = email.strip().lower()
        if email in [
            address.lower() for address in self.blacklisted_email_addresses.split()
        ]:
            return True

        domain = email.split("@")[1]
        return domain in [
            domain.lower() for domain in self.blacklisted_email_domains.split()
        ]


class Membership(TimeStampedModel):
    class Role(models.TextChoices):
        MEMBER = "member", _("Member")
        MODERATOR = "moderator", _("Moderator")
        ADMIN = "admin", _("Admin")

    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    role = models.CharField(
        choices=Role.choices, max_length=9, default=Role.MEMBER, db_index=True
    )
    active = models.BooleanField(default=True)

    objects = MembershipManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["member", "community"], name="unique_membership"
            )
        ]
        indexes = [models.Index(fields=["member", "community", "active"])]

    def __str__(self):
        return self.get_role_display()

    def get_absolute_url(self):
        return reverse("communities:membership_detail", args=[self.id])

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_moderator(self):
        return self.role == self.Role.MODERATOR

    def is_member(self):
        return self.role == self.Role.MEMBER
