from typing import Optional

from django.conf import settings
from django.core.validators import RegexValidator, URLValidator
from django.db import models
from django.http import HttpRequest
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

ROLES = (
    ("member", _("Member")),
    ("moderator", _("Moderator")),
    ("admin", _("Admin")),
)


class CommunityManager(models.Manager):
    use_in_migrations = True

    def get_current(self, request: HttpRequest) -> Optional["Community"]:
        """
        Returns the current community linked to the site domain. Community
        must be active.
        """
        try:
            return self.get(active=True, domain__iexact=request.get_host())
        except self.model.DoesNotExist:
            return None


class Community(TimeStampedModel):
    domain = models.CharField(
        unique=True,
        max_length=100,
        validators=[
            RegexValidator(
                regex=URLValidator.host_re,
                message=_("This is not a valid domain"),
            )
        ],
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

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

    def user_has_role(self, user: settings.AUTH_USER_MODEL, role: str) -> bool:
        if user.is_anonymous:
            return False
        # cache for this user
        if not hasattr(user, "_community_roles_cache"):
            user._community_roles_cache = dict(
                Membership.objects.filter(
                    active=True, member=user
                ).values_list("community", "role")
            )
        try:
            return user._community_roles_cache[self.id] == role
        except KeyError:
            return False


class Membership(TimeStampedModel):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    role = models.CharField(choices=ROLES, max_length=9, default="member")
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("community", "member")

    def __str__(self) -> str:
        return self.get_role_display()
