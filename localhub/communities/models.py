# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from dataclasses import dataclass
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.validators import RegexValidator, URLValidator
from django.db import models
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords
from sorl.thumbnail import ImageField

from localhub.activities.utils import extract_hashtags
from localhub.db.search import SearchQuerySetMixin
from localhub.markdown.fields import MarkdownField

DOMAIN_VALIDATOR = RegexValidator(
    regex=URLValidator.host_re, message=_("This is not a valid domain")
)


@dataclass
class RequestCommunity:
    """
    This works in a similar way to Django auth AnonymousUser, if
    no community present. It provides ducktyping so we don't have to check
    for None everywhere. Wraps HttpRequest/Site.
    """

    request: HttpRequest

    name: str
    domain: str

    id = None
    pk = None

    active: bool = False

    def get_absolute_url(self):
        return self.request.full_path

    def user_has_role(self, user, *roles):
        return False

    def is_member(self, user):
        return False

    def is_moderator(self, user):
        return False

    def is_admin(self, user):
        return False


class CommunityQuerySet(models.QuerySet):
    def with_num_members(self):
        return self.annotate(num_members=models.Count("membership"))

    def with_is_member(self, user):
        if user.is_authenticated:
            return self.annotate(
                is_member=models.Exists(
                    self.model.objects.filter(
                        membership__member=user,
                        membership__active=True,
                        membership__community=models.OuterRef("pk"),
                    )
                ),
                member_role=models.Subquery(
                    Membership.objects.filter(
                        member=user, active=True, community=models.OuterRef("pk"),
                    ).values("role")[:1],
                ),
            )
        return self.annotate(
            is_member=models.Value(False, output_field=models.BooleanField()),
            member_role=models.Value(None, output_field=models.CharField()),
        )

    def visible(self, user):
        """
        Returns all communities either listed publicly or where user is a member
        """
        return (
            self.with_is_member(user)
            .filter(models.Q(models.Q(is_member=True) | models.Q(public=True)))
            .distinct()
        )

    def get_current(self, request):
        """
        Returns current community matching request domain if active.
        """
        try:
            return self.get(active=True, domain__iexact=request.get_host())
        except self.model.DoesNotExist:
            site = get_current_site(request)
            return RequestCommunity(request, site.name, site.domain)


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

    history = HistoricalRecords()

    public = models.BooleanField(default=True)

    allow_join_requests = models.BooleanField(default=True)

    blacklisted_email_domains = models.TextField(blank=True)

    blacklisted_email_addresses = models.TextField(blank=True)

    objects = CommunityQuerySet.as_manager()

    class Meta:
        verbose_name_plural = _("Communities")

    def __str__(self):
        return self.name

    @property
    def _history_user(self):
        return self.admin

    @_history_user.setter
    def _history_user(self, value):
        self.admin = value

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

    def get_members_by_role(self, *roles):
        return self.members.filter(membership__role__in=roles)

    def get_members(self):
        return self.get_members_by_role(
            Membership.Role.MEMBER, Membership.Role.MODERATOR, Membership.Role.ADMIN,
        )

    def get_moderators(self):
        return self.get_members_by_role(
            Membership.Role.MODERATOR, Membership.Role.ADMIN
        )

    def get_admins(self):
        return self.get_members_by_role(Membership.Role.ADMIN)

    def user_has_role(self, user, *roles):
        if user.is_anonymous:
            return False
        return user.has_role(self, *roles)

    def is_member(self, user):
        return self.user_has_role(
            user,
            Membership.Role.MEMBER,
            Membership.Role.MODERATOR,
            Membership.Role.ADMIN,
        )

    def is_moderator(self, user):
        return self.user_has_role(
            user, Membership.Role.MODERATOR, Membership.Role.ADMIN
        )

    def is_admin(self, user):
        return self.user_has_role(user, Membership.Role.ADMIN)

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


class MembershipQuerySet(SearchQuerySetMixin, models.QuerySet):
    search_document_field = "member__search_document"


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

    objects = MembershipQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["member", "community"], name="unique_membership"
            )
        ]
        indexes = [models.Index(fields=["member", "community", "active"])]

    def __str__(self):
        return self.get_role_display()

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_moderator(self):
        return self.role == self.Role.MODERATOR

    def is_member(self):
        return self.role == self.Role.MEMBER
