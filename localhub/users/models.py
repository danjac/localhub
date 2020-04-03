# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from sorl.thumbnail import ImageField
from taggit.models import Tag
from timezone_field import TimeZoneField

from localhub.communities.models import Membership
from localhub.db.content_types import get_generic_related_queryset
from localhub.db.fields import ChoiceArrayField
from localhub.db.search import SearchIndexer, SearchQuerySetMixin
from localhub.db.tracker import Tracker
from localhub.markdown.fields import MarkdownField
from localhub.notifications.decorators import dispatch
from localhub.notifications.models import Notification
from localhub.utils.itertools import takefirst

from .utils import user_display


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

    def with_num_unread_messages(self, recipient):
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

    def with_role(self, community):
        """Adds annotations "role" and "role_display" for users for this community.
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
            username, email, password, is_staff=True, is_superuser=True, **kwargs
        )


class User(AbstractUser):
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

    history = HistoricalRecords()

    follower_notification_tracker = Tracker(["avatar", "name", "bio"])

    objects = UserManager()

    class Meta(AbstractUser.Meta):

        indexes = [
            GinIndex(fields=["search_document"]),
            models.Index(fields=["name", "username", "email"]),
        ]

    @cached_property
    def community_roles_cache(self):
        """
        Returns:
            cached dict of roles as {community_id:role}
        """
        return dict(
            Membership.objects.filter(active=True, member=self).values_list(
                "community", "role"
            )
        )

    def get_absolute_url(self):
        return reverse("users:activities", args=[self.username])

    def get_display_name(self):
        """Displays full name or username

        Returns: str:  full display name
        """

        return user_display(self)

    def get_notifications(self):
        """Returns notifications where the user is the target content object,
        *not* necessarily the actor or recipient.

        Returns:
            QuerySet
        """
        return get_generic_related_queryset(self, Notification)

    def has_role(self, community, *roles):
        """Checks if user has given role in the community, if any. Result
        is cached.
        Args:
            community (Community)
            *roles: roles i.e. one or more of "member", "moderator", "admin"

        Returns:
            bool: if user has any of these roles
        """
        return self.community_roles_cache.get(community.id, None) in roles

    def has_inactive_membership(self, community):
        """Checks if user has an inactive membership for this community.
        """
        return Membership.objects.filter(
            community=community, member=self, active=False,
        ).exists()

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

        if self.follower_notification_tracker.changed():
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
