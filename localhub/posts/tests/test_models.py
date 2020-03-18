# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from taggit.models import Tag

from localhub.comments.factories import CommentFactory
from localhub.comments.models import Comment
from localhub.communities.factories import MembershipFactory
from localhub.communities.models import Membership
from localhub.likes.factories import LikeFactory
from localhub.notifications.factories import NotificationFactory
from localhub.users.factories import UserFactory

from ..factories import PostFactory
from ..models import Post

pytestmark = pytest.mark.django_db


class TestPostModel:
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

    def test_delete_comments_on_delete(self, post):
        CommentFactory(content_object=post)
        post.delete()
        assert Comment.objects.count() == 0

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
            community=community, role=Membership.ROLES.moderator
        ).member

        moderator = MembershipFactory(
            community=community, role=Membership.ROLES.moderator, member=UserFactory(),
        ).member

        mentioned = MembershipFactory(
            member=UserFactory(username="danjac"),
            community=community,
            role=Membership.ROLES.member,
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
        assert len(notifications) == 4

        assert notifications[0].recipient == mentioned
        assert notifications[0].actor == post.owner
        assert notifications[0].verb == "mention"

        assert notifications[1].recipient == tag_follower
        assert notifications[1].actor == post.owner
        assert notifications[1].verb == "followed_tag"

        assert notifications[2].recipient == user_follower
        assert notifications[2].actor == post.owner
        assert notifications[2].verb == "followed_user"

        assert notifications[3].recipient == moderator
        assert notifications[3].actor == post.owner
        assert notifications[3].verb == "moderator_review"

    def test_notify_on_delete(self, post, moderator, send_webpush_mock):
        notifications = post.notify_on_delete(moderator.member)

        assert len(notifications) == 1
        assert notifications[0].recipient == post.owner
        assert notifications[0].actor == moderator.member
        assert notifications[0].verb == "delete"

    def test_notify_on_update(self, community, send_webpush_mock):

        owner = MembershipFactory(
            community=community, role=Membership.ROLES.moderator, member=UserFactory(),
        ).member

        moderator = MembershipFactory(
            community=community, role=Membership.ROLES.moderator, member=UserFactory(),
        ).member

        post = PostFactory(
            owner=owner,
            community=community,
            description="hello @danjac from @owner #movies #reviews",
        )

        notifications = post.notify_on_update()
        assert len(notifications) == 1

        assert notifications[0].recipient == moderator
        assert notifications[0].actor == post.owner
        assert notifications[0].verb == "moderator_review"

    def test_notify_on_create_reshare(self, community):

        mentioned = MembershipFactory(
            member=UserFactory(username="danjac"),
            community=community,
            role=Membership.ROLES.member,
        ).member

        # ensure we just have one notification for multiple tags

        movies = Tag.objects.create(name="movies")
        reviews = Tag.objects.create(name="reviews")

        tag_follower = MembershipFactory(
            community=community, member=UserFactory(),
        ).member
        tag_follower.following_tags.add(movies, reviews)

        assert tag_follower.following_tags.count() == 2

        owner = MembershipFactory(
            community=community, role=Membership.ROLES.moderator, member=UserFactory(),
        ).member

        moderator = MembershipFactory(
            community=community, role=Membership.ROLES.moderator, member=UserFactory(),
        ).member

        post = PostFactory(
            owner=owner,
            community=community,
            description="hello @danjac from @owner #movies #reviews",
        )

        # reshare
        reshare = post.reshare(UserFactory())
        notifications = list(reshare.notify_on_create())
        assert len(notifications) == 4

        assert notifications[0].recipient == mentioned
        assert notifications[0].actor == reshare.owner
        assert notifications[0].verb == "mention"

        assert notifications[1].recipient == tag_follower
        assert notifications[1].actor == reshare.owner
        assert notifications[1].verb == "followed_tag"

        assert notifications[2].recipient == post.owner
        assert notifications[2].actor == reshare.owner
        assert notifications[2].verb == "reshare"

        assert notifications[3].recipient == moderator
        assert notifications[3].actor == reshare.owner
        assert notifications[3].verb == "moderator_review"

    def test_fetch_opengraph_data_from_url_if_ok(self, mocker):
        class MockHeadResponse:
            ok = True
            url = "https://google.com"

        class MockResponse:
            ok = True
            headers = {"Content-Type": "text/html; charset=utf-8"}
            content = """
<html>
<head>
<title>Hello</title>
<meta property="og:title" content="a test site">
<meta property="og:image" content="http://example.com/test.jpg">
<meta property="og:description" content="test description">
</head>
<body>
</body>
</html>"""

        mocker.patch("requests.head", lambda url, **kwargs: MockHeadResponse)
        mocker.patch("requests.get", lambda url, **kwargs: MockResponse)
        post = PostFactory(url="http://google.com", title="", description="")
        post.fetch_opengraph_data_from_url()

        assert post.url == "https://google.com"
        assert post.title == "a test site"
        assert post.opengraph_image == "http://example.com/test.jpg"
        assert post.opengraph_description == "test description"

    def test_fetch_opengraph_data_from_url_if_not_ok(self, mocker):
        class MockHeadResponse:
            ok = True
            url = "https://google.com"

        class MockResponse:
            ok = False

        mocker.patch("requests.head", lambda url, **kwargs: MockHeadResponse)
        mocker.patch("requests.get", lambda url, **kwargs: MockResponse)
        post = PostFactory(url="http://google.com", title="", description="")
        post.fetch_opengraph_data_from_url()

        assert post.url == "https://google.com"
        assert post.title == "google.com"
        assert post.opengraph_image == ""
        assert post.opengraph_description == ""

    def test_if_not_html(self, mocker):
        class MockHeadResponse:
            ok = True
            url = "https://google.com"

        class MockResponse:
            ok = True
            headers = {"Content-Type": "image/jpeg"}

        mocker.patch("requests.head", lambda url, **kwargs: MockHeadResponse)
        mocker.patch("requests.get", lambda url, **kwargs: MockResponse)
        post = PostFactory(url="http://google.com/test.jpg", title="", description="")
        post.fetch_opengraph_data_from_url()

        assert post.url == "https://google.com"
        assert post.title == "google.com"
        assert post.opengraph_image == ""
        assert post.opengraph_description == ""

    def test_get_opengraph_image_if_safe_if_https_img(self):
        post = Post(opengraph_image="https://imgur.com/img.jpg")
        assert post.get_opengraph_image_if_safe() == "https://imgur.com/img.jpg"

    def test_get_opengraph_image_if_safe_if_http_img(self):
        post = Post(opengraph_image="http://imgur.com/img.jpg")
        assert post.get_opengraph_image_if_safe() == ""

    def test_get_opengraph_image_if_safe_if_not_valid_img(self):
        post = Post(opengraph_image="https://imgur.com/img.txt")
        assert post.get_opengraph_image_if_safe() == ""

    def test_get_opengraph_image_if_safe_if_empty(self):
        post = Post(opengraph_image="")
        assert post.get_opengraph_image_if_safe() == ""

    def test_soft_delete(self, post):
        CommentFactory(content_object=post)
        NotificationFactory(content_object=post)
        # FlagFactory(content_object=post)
        LikeFactory(content_object=post)

        post.soft_delete()
        post.refresh_from_db()

        assert post.published is None
        assert post.deleted is not None

        assert post.get_notifications().count() == 0
        assert post.get_likes().count() == 0
        assert post.get_flags().count() == 0
        assert post.get_comments().count() == 0
