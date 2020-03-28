# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.urls import reverse
from taggit.models import Tag

from localhub.comments.factories import CommentFactory
from localhub.comments.models import Comment
from localhub.communities.factories import MembershipFactory
from localhub.communities.models import Membership
from localhub.flags.factories import FlagFactory
from localhub.likes.factories import LikeFactory
from localhub.notifications.factories import NotificationFactory
from localhub.users.factories import UserFactory

from ..factories import PostFactory
from ..models import Post

pytestmark = pytest.mark.django_db


class TestPostModel:
    def test_get_page_title_segments_for_model(self):
        segments = Post.get_page_title_segments_for_model()
        assert segments == ["Posts"]

    def test_get_page_title_segments_for_instance(self, post):
        segments = post.get_page_title_segments()
        assert len(segments) == 2
        assert segments[0] == "Posts"

    def test_get_page_title_segments_for_instance_with_extra_segments(self, post):
        segments = post.get_page_title_segments(["Edit"])
        assert len(segments) == 3
        assert segments[0] == "Posts"
        assert segments[2] == "Edit"

    def test_get_breadcrumbs_for_model(self):
        breadcrumbs = Post.get_breadcrumbs_for_model()
        assert len(breadcrumbs) == 1

        assert breadcrumbs[0][0] == reverse("posts:list")

    def test_get_breadcrumbs_for_instance(self, post):
        breadcrumbs = post.get_breadcrumbs()
        assert len(breadcrumbs) == 2

        assert breadcrumbs[0][0] == reverse("posts:list")
        assert breadcrumbs[1][0] == post.get_absolute_url()

    def test_get_breadcrumbs_for_instance_with_extra_segments(self, post):
        breadcrumbs = post.get_breadcrumbs([(None, "Comments")])
        assert len(breadcrumbs) == 3

        assert breadcrumbs[0][0] == reverse("posts:list")
        assert breadcrumbs[1][0] == post.get_absolute_url()
        assert breadcrumbs[2][0] is None
        assert breadcrumbs[2][1] == "Comments"

    def test_get_breadcrumbs_for_instance_if_draft(self, post):
        post.published = None
        breadcrumbs = post.get_breadcrumbs()
        assert len(breadcrumbs) == 2

        assert breadcrumbs[0][0] == reverse("activities:drafts")
        assert breadcrumbs[1][0] == post.get_absolute_url()

    def test_get_absolute_url(self):
        """
        If non-ASCII slug append to url
        """
        post = PostFactory(title="test post")
        assert post.get_absolute_url() == f"/posts/{post.id}/test-post/"

    def test_get_absolute_url_if_non_ascii(self):
        """
        If non-ASCII slug is empty just use ID
        """
        post = PostFactory(title="中国研究方法")
        assert post.get_absolute_url() == f"/posts/{post.id}/zhong-guo-yan-jiu-fang-fa/"

    def test_extract_tags(self):

        post = Post(title="something #movies", description="content #movies and #films")
        assert post.extract_tags() == {"movies", "films"}

    def test_save_tags(self, post):

        post.description = "a post about #movies"
        post.save()

        tags = [t.name for t in post.tags.all()]
        assert "movies" in tags

        # clear tags
        post.description = "a post about movies"
        post.save()
        assert post.tags.count() == 0

    def test_reshare(self, post, user):

        reshared = post.reshare(user)
        assert reshared.title == post.title
        assert reshared.description == post.description
        assert reshared.is_reshare
        assert reshared.parent == post
        assert reshared.community == post.community
        assert reshared.owner == user
        assert reshared.published

    def test_update_reshares(self, post, user):

        reshared = post.reshare(user)
        post.title = "a new title"
        post.save()
        post.update_reshares()
        reshared.refresh_from_db()
        assert reshared.title == "a new title"

    def test_reshare_a_reshare(self, post, user):

        reshared = post.reshare(user)
        reshared.reshare(UserFactory())

        assert reshared.title == post.title
        assert reshared.description == post.description
        assert reshared.is_reshare
        assert reshared.parent == post
        assert reshared.community == post.community
        assert reshared.owner == user
        assert reshared.published

    def test_manage_comments_on_delete(self, post):
        # comment relations should be set to NULL.
        CommentFactory(content_object=post)
        post.delete()
        assert Comment.objects.count() == 1
        comment = Comment.objects.first()
        assert comment.object_id is None
        assert comment.content_type is None
        assert comment.content_object is None

    def test_get_domain_if_no_url(self):
        assert Post().get_domain() == ""

    def test_get_domain_if_url(self):
        assert Post(url="http://google.com").get_domain() == "google.com"

    def test_get_content_warning_tags_if_any(self):
        post = PostFactory(description="This post is #nsfw!")
        assert post.get_content_warning_tags() == {"nsfw"}

    def test_get_content_warning_tags_if_none(self):
        post = PostFactory(description="This post is #legit")
        assert post.get_content_warning_tags() == set()

    def test_notify_on_create(self, community, send_webpush_mock):
        # owner should not receive any notifications from their own posts
        owner = MembershipFactory(
            community=community, role=Membership.Role.MODERATOR
        ).member

        mentioned = MembershipFactory(
            member=UserFactory(username="danjac"),
            community=community,
            role=Membership.Role.MEMBER,
        ).member

        # ensure we just have one notification for multiple tags

        movies = Tag.objects.create(name="movies")
        reviews = Tag.objects.create(name="reviews")

        post = PostFactory(
            owner=owner,
            community=community,
            description="hello @danjac from @owner #movies #reviews",
        )

        tag_follower = MembershipFactory(
            community=community, member=UserFactory(),
        ).member
        tag_follower.following_tags.add(movies, reviews)

        # owner should also follow tags to ensure they aren't notified
        owner.following_tags.add(movies, reviews)

        assert tag_follower.following_tags.count() == 2

        user_follower = MembershipFactory(
            community=community, member=UserFactory(),
        ).member
        user_follower.following.add(post.owner)

        notifications = post.notify_on_create()
        assert len(notifications) == 3

        assert notifications[0].recipient == mentioned
        assert notifications[0].actor == post.owner
        assert notifications[0].verb == "mention"

        assert notifications[1].recipient == tag_follower
        assert notifications[1].actor == post.owner
        assert notifications[1].verb == "followed_tag"

        assert notifications[2].recipient == user_follower
        assert notifications[2].actor == post.owner
        assert notifications[2].verb == "followed_user"

    def test_notify_on_delete(self, post, moderator, send_webpush_mock):
        notifications = post.notify_on_delete(moderator.member)

        assert len(notifications) == 1
        assert notifications[0].recipient == post.owner
        assert notifications[0].actor == moderator.member
        assert notifications[0].verb == "delete"

    def test_notify_on_update(self, community, send_webpush_mock):

        owner = MembershipFactory(community=community).member

        member = MembershipFactory(
            community=community, member=UserFactory(username="danjac"),
        ).member

        post = PostFactory(
            owner=owner,
            community=community,
            description="hello from @owner #movies #reviews",
        )

        post.description = "hello @danjac"
        post.save()

        notifications = post.notify_on_update()
        assert len(notifications) == 1

        assert notifications[0].recipient == member
        assert notifications[0].actor == post.owner
        assert notifications[0].verb == "mention"

    def test_notify_on_create_reshare(self, community):

        mentioned = MembershipFactory(
            member=UserFactory(username="danjac"),
            community=community,
            role=Membership.Role.MEMBER,
        ).member

        # ensure we just have one notification for multiple tags

        movies = Tag.objects.create(name="movies")
        reviews = Tag.objects.create(name="reviews")

        tag_follower = MembershipFactory(
            community=community, member=UserFactory(),
        ).member
        tag_follower.following_tags.add(movies, reviews)

        assert tag_follower.following_tags.count() == 2

        owner = MembershipFactory(community=community,).member

        post = PostFactory(
            owner=owner,
            community=community,
            description="hello @danjac from @owner #movies #reviews",
        )

        # reshare
        reshare = post.reshare(UserFactory())
        notifications = list(reshare.notify_on_create())
        assert len(notifications) == 3

        assert notifications[0].recipient == mentioned
        assert notifications[0].actor == reshare.owner
        assert notifications[0].verb == "mention"

        assert notifications[1].recipient == tag_follower
        assert notifications[1].actor == reshare.owner
        assert notifications[1].verb == "followed_tag"

        assert notifications[2].recipient == post.owner
        assert notifications[2].actor == reshare.owner
        assert notifications[2].verb == "reshare"

    def test_soft_delete(self, post, mocker):
        CommentFactory(content_object=post)
        NotificationFactory(content_object=post)
        FlagFactory(content_object=post)
        LikeFactory(content_object=post)

        with mocker.patch(
            "localhub.activities.signals.soft_delete"
        ) as mock_soft_delete:
            post.soft_delete()
            assert mock_soft_delete.called_with(sender=Post, instance=post)

        post.refresh_from_db()

        assert post.published is None
        assert post.deleted is not None

        # comments should NOT be deleted but refs should be removed

        assert Comment.objects.count() == 1
        assert post.get_comments().count() == 0
        assert post.get_notifications().count() == 0
        assert post.get_likes().count() == 0
        assert post.get_flags().count() == 0

    def test_get_comment_url(self, post):
        assert post.get_comment_url() == reverse("posts:comment", args=[post.id])

    def test_get_delete_url(self, post):
        assert post.get_delete_url() == reverse("posts:delete", args=[post.id])

    def test_get_dislike_url(self, post):
        assert post.get_dislike_url() == reverse("posts:dislike", args=[post.id])

    def test_get_flag_url(self, post):
        assert post.get_flag_url() == reverse("posts:flag", args=[post.id])

    def test_get_like_url(self, post):
        assert post.get_like_url() == reverse("posts:like", args=[post.id])

    def test_get_pin_url(self, post):
        assert post.get_pin_url() == reverse("posts:pin", args=[post.id])

    def test_get_publish_url(self, post):
        assert post.get_publish_url() == reverse("posts:publish", args=[post.id])

    def test_get_reshare_url(self, post):
        assert post.get_reshare_url() == reverse("posts:reshare", args=[post.id])

    def test_get_unpin_url(self, post):
        assert post.get_unpin_url() == reverse("posts:unpin", args=[post.id])

    def test_get_update_url(self, post):
        assert post.get_update_url() == reverse("posts:update", args=[post.id])

    def test_get_bookmark_url(self, post):
        assert post.get_bookmark_url() == reverse("posts:bookmark", args=[post.id])

    def test_get_remove_bookmark_url(self, post):
        assert post.get_remove_bookmark_url() == reverse(
            "posts:remove_bookmark", args=[post.id]
        )
