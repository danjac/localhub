# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from sorl.thumbnail import ImageField
from taggit.models import Tag
from timezone_field import TimeZoneField

from localhub.communities.models import Membership
from localhub.db.content_types import (
    get_generic_related_queryset,
)
from localhub.db.fields import ChoiceArrayField
from localhub.db.search import SearchIndexer, SearchQuerySetMixin
from localhub.markdown.fields import MarkdownField
from localhub.notifications.models import Notification


class UserQuerySet(SearchQuerySetMixin, models.QuerySet):
    def for_email(self, email):
        """
        Returns all users with primary or additional emails matching
        this email (case insensitive).
        """
        return self.filter(
            models.Q(emailaddress__email__iexact=email) | models.Q(email__iexact=email)
        )

    def with_notification_prefs(self, *prefs):
        return self.filter(notification_preferences__contains=list(prefs))

    def with_is_following(self, follower):
        return self.annotate(
            is_following=models.Exists(
                follower.following.filter(pk=models.OuterRef("id"))
            )
        )

    def with_is_blocked(self, user):
        return self.annotate(
            is_blocked=models.Exists(user.blocked.filter(pk=models.OuterRef("id")))
        )

    def matches_usernames(self, names):
        """
        Returns any users matching username (case insensitive).
        """
        if not names:
            return self.none()
        return self.filter(username__iregex=r"^(%s)+" % "|".join(names))

    def for_community(self, community):
        """
        Returns only users which are a) active and b) have active
        membership with given community.
        """

        return self.filter(
            membership__community=community, membership__active=True, is_active=True,
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

    HOME_PAGE_FILTERS = Choices(
        ("users", _("Posts, events and photots from people I'm following")),
        ("tags", _("Posts, events and photos containing tags I'm following")),
    )

    NOTIFICATION_PREFERENCES = Choices(
        ("new_message", _("I receive a direct message")),
        ("new_follower", _("Someone starts following me")),
        ("new_member", _("Someone joins a community I belong to")),
        ("new_comment", _("Someone comments on my post, event or photo")),
        (
            "new_sibling_comment",
            _(
                "Someone comments on a post, event or photo I've also commented on"  # noqa
            ),
        ),
        ("reshare", _("Someone has reshared my post, event or photo")),
        ("mention", _("I am @mentioned in a post, event, photo or comment")),
        (
            "moderator_delete",
            _("A moderator deletes my post, event, photo or comment"),
        ),
        ("moderator_edit", _("A moderator edits my post, event, photo or comment"),),
        ("like", _("Someone likes my post, event, photo or comment")),
        (
            "new_followed_user_post",
            _("Someone I'm following submits a post, event or photo"),
        ),
        ("replied_to_comment", _("Someone replies to my comment")),
        ("new_followed_user_comment", _("Someone I'm following submits a comment"),),
        (
            "new_followed_tag_post",
            _(
                "A post, event or photo is submitted containing tags I'm following"  # noqa
            ),
        ),
        (
            "flag",
            _(
                "A user has flagged a comment, post, event or photo (moderators only)"  # noqa
            ),
        ),
        (
            "moderator_review_request",
            _(
                "A user has a new comment, post, event or photo for you to "
                "review (moderators only)"
            ),
        ),
    )

    name = models.CharField(_("Full name"), blank=True, max_length=255)
    bio = MarkdownField(blank=True)
    avatar = ImageField(upload_to="avatars", null=True, blank=True)

    language = models.CharField(
        max_length=6,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        help_text=_("Preferred language. User content will not be translated."),
    )

    default_timezone = TimeZoneField(default=settings.TIME_ZONE)

    home_page_filters = ChoiceArrayField(
        models.CharField(max_length=12, choices=HOME_PAGE_FILTERS),
        default=list,
        blank=True,
    )

    show_sensitive_content = models.BooleanField(default=False)
    show_embedded_content = models.BooleanField(default=False)

    notification_preferences = ChoiceArrayField(
        models.CharField(max_length=30, choices=NOTIFICATION_PREFERENCES),
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

    search_document = SearchVectorField(null=True, editable=False)

    search_indexer = SearchIndexer(("A", "username"), ("B", "name"))

    objects = UserManager()

    class Meta(AbstractUser.Meta):

        indexes = [
            GinIndex(fields=["search_document"]),
            models.Index(fields=["name", "username", "email"]),
        ]

    def get_absolute_url(self):
        return reverse("users:activities", args=[self.username])

    def has_notification_pref(self, pref):
        return (
            pref in self.notification_preferences
            if self.notification_preferences
            else False
        )

    def get_notifications(self):
        """
        Note: returns notifications triggered by this user, not
        received by this user.
        """
        return get_generic_related_queryset(self, Notification)

    def has_role(self, community, *roles):
        """
        Checks if user has given role in the community, if any. Result
        is cached.
        """
        return self.community_roles_cache.get(community.id, None) in roles

    @cached_property
    def community_roles_cache(self):
        return dict(
            Membership.objects.filter(active=True, member=self).values_list(
                "community", "role"
            )
        )

    def notify_on_join(self, community):
        notifications = [
            Notification(
                content_object=self,
                actor=self,
                recipient=member,
                community=community,
                verb="new_member",
            )
            for member in community.members.with_notification_prefs(
                "new_member"
            ).exclude(pk=self.pk)
        ]
        return Notification.objects.bulk_create(notifications)

    def notify_on_follow(self, recipient, community):
        """
        Sends notification to provided recipients
        """

        notifications = [
            Notification.objects.create(
                content_object=self,
                actor=self,
                recipient=recipient,
                community=community,
                verb="new_follower",
            )
        ]

        return notifications
