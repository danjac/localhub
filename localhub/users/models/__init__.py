# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models, transaction
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from sorl.thumbnail import ImageField
from taggit.models import Tag
from timezone_field import TimeZoneField

from localhub.communities.models import Membership
from localhub.db.fields import ChoiceArrayField
from localhub.db.generic import get_generic_related_queryset
from localhub.db.search.indexer import SearchIndexer
from localhub.db.tracker import TrackerModelMixin
from localhub.markdown.fields import MarkdownField
from localhub.notifications.decorators import dispatch
from localhub.notifications.models import Notification
from localhub.utils.itertools import takefirst

from .managers import UserManager


class User(TrackerModelMixin, AbstractUser):
    class ActivityStreamFilters(models.TextChoices):
        USERS = "users", _("Limited to only content from people I'm following")
        TAGS = "tags", _("Limited to only tags I'm following")

    name = models.CharField(_("Full name"), blank=True, max_length=255)
    bio = MarkdownField(blank=True)
    avatar = ImageField(upload_to="avatars", null=True, blank=True)

    language = models.CharField(
        max_length=6, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE,
    )

    default_timezone = TimeZoneField(default=settings.TIME_ZONE)

    activity_stream_filters = ChoiceArrayField(
        models.CharField(max_length=12, choices=ActivityStreamFilters.choices),
        default=list,
        blank=True,
    )

    show_external_images = models.BooleanField(default=True)
    show_sensitive_content = models.BooleanField(default=False)
    show_embedded_content = models.BooleanField(default=False)

    send_email_notifications = models.BooleanField(default=True)

    dismissed_notices = ArrayField(models.CharField(max_length=30), default=list)

    following = models.ManyToManyField(
        "self", related_name="followers", blank=True, symmetrical=False
    )

    blocked = models.ManyToManyField(
        "self", related_name="blockers", blank=True, symmetrical=False
    )

    following_tags = models.ManyToManyField(Tag, related_name="+", blank=True)

    blocked_tags = models.ManyToManyField(Tag, related_name="+", blank=True)

    search_document = SearchVectorField(null=True, editable=False)

    search_indexer = SearchIndexer(("A", "username"), ("B", "name"), ("C", "bio"))

    tracked_fields = ["avatar", "name", "bio"]

    objects = UserManager()

    class Meta(AbstractUser.Meta):

        indexes = [
            GinIndex(fields=["search_document"]),
            models.Index(fields=["name", "username", "email"]),
        ]

    def get_absolute_url(self):
        return reverse("users:activities", args=[self.username])

    def get_display_name(self):
        """Displays full name or username

        Returns: str:  full display name
        """
        return self.name or self.username

    def get_initials(self):
        return "".join([n[0].upper() for n in self.get_display_name().split()][:2])

    def get_notifications(self):
        """Returns notifications where the user is the target content object,
        *not* necessarily the actor or recipient.

        Returns:
            QuerySet
        """
        return get_generic_related_queryset(self, Notification)

    @cached_property
    def member_cache(self):
        """
        Returns:
            A dict of membership status/roles:
            {
                "active": {community_id: "admin"}, ...
                "inactive": [list of community ids...]
            }
        """
        dct = {"active": {}, "inactive": []}

        for community_id, role, active in Membership.objects.filter(
            member=self
        ).values_list("community", "role", "active"):
            if active:
                dct["active"][community_id] = role
            else:
                dct["inactive"].append(community_id)
        return dct

    def has_role(self, community, *roles):
        """Checks if user has given role in the community, if any. Result
        is cached.
        Args:
            community (Community)
            *roles: roles i.e. one or more of "member", "moderator", "admin"

        Returns:
            bool: if user has any of these roles
        """
        try:
            return self.member_cache["active"][community.id] in roles
        except KeyError:
            return False

    def is_inactive_member(self, community):
        """Checks if user has an inactive membership for this community.
        """
        return community.id in self.member_cache["inactive"]

    def is_blocked(self, user):
        """ Check if user is blocking this other user, or is blocked by this other
        user.

        Args:
            user (User)

        Returns:
            bool
        """
        if self == user:
            return False
        return self.get_blocked_users().filter(pk=user.id).exists()

    def get_blocked_users(self):
        """Return a) users I'm blocking and b) users blocking me.

        Returns:
            QuerySet
        """
        return (self.blockers.all() | self.blocked.all()).distinct()

    @transaction.atomic
    def block_user(self, user):
        """Blocks this user. Any following relationships are also removed.

        Args:
            user (User)
        """
        self.blocked.add(user)
        self.following.remove(user)
        self.followers.remove(user)

    @dispatch
    def notify_on_join(self, community):
        """Returns notification to all other current members that
        this user has just joined the community.

        Args:
            community (Community)

        Returns:
            list: list of Notification instances
        """
        return [
            Notification(
                content_object=self,
                actor=self,
                recipient=member,
                community=community,
                verb="new_member",
            )
            for member in community.members.exclude(pk=self.pk)
        ]

    @dispatch
    def notify_on_follow(self, recipient, community):
        """Sends notification to recipient that they have just been followed.

        Args:
            recipient (User)
            community (Community)

        Returns:
            Notification
        """
        return Notification(
            content_object=self,
            actor=self,
            recipient=recipient,
            community=community,
            verb="new_follower",
        )

    @dispatch
    def notify_on_update(self):
        """Sends notification to followers that user has updated their profile.

        This is sent to followers across all communities where the user is
        an active member.

        If follower belongs to multiple common communities, we just send
        notification to one community.

        We only send notifications if certain tracked fields are updated
        e.g. bio or avatar.

        Returns:
            list: Notifications to followers
        """

        if self.has_tracker_changed():
            return takefirst(
                [
                    Notification(
                        content_object=self,
                        actor=self,
                        recipient=follower,
                        community=membership.community,
                        verb="update",
                    )
                    for membership in self.membership_set.filter(
                        active=True
                    ).select_related("community")
                    for follower in self.followers.for_community(membership.community)
                ],
                lambda n: n.recipient,
            )

    def get_email_addresses(self):
        """Get set of emails belonging to user.

        Returns:
            set: set of email addresses
        """
        return set([self.email]) | set(
            self.emailaddress_set.values_list("email", flat=True)
        )

    def dismiss_notice(self, notice):
        """
        Adds notice permanently to list of dismissed notices.

        Args:
            notice (str): unique notice ID e.g. "private-stash"
        """
        if notice not in self.dismissed_notices:
            self.dismissed_notices.append(notice)
            self.save(update_fields=["dismissed_notices"])
