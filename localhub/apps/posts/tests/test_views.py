# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.urls import reverse

# Third Party Libraries
import pytest

# Localhub
from localhub.apps.bookmarks.factories import BookmarkFactory
from localhub.apps.bookmarks.models import Bookmark
from localhub.apps.comments.models import Comment
from localhub.apps.communities.factories import MembershipFactory
from localhub.apps.communities.models import Membership
from localhub.apps.flags.models import Flag
from localhub.apps.likes.factories import LikeFactory
from localhub.apps.likes.models import Like
from localhub.apps.notifications.factories import NotificationFactory
from localhub.apps.notifications.models import Notification
from localhub.apps.users.factories import UserFactory

# Local
from ..factories import PostFactory
from ..models import Post

pytestmark = pytest.mark.django_db


@pytest.fixture
def post_for_member(member):
    return PostFactory(owner=member.member, community=member.community)


class TestPostListView:
    def test_get(self, client, member):
        PostFactory.create_batch(3, community=member.community, owner=member.member)
        response = client.get(reverse("posts:list"))
        assert len(response.context["object_list"]) == 3

    @pytest.mark.django_db(transaction=True)
    def test_search(self, client, member):
        PostFactory.create_batch(
            3, community=member.community, owner=member.member, title="testme"
        )

        response = client.get(reverse("posts:list"), {"q": "testme"})
        assert len(response.context["object_list"]) == 3


class TestPostCreateView:
    def test_get(self, client, member):
        response = client.get(reverse("posts:create"))
        assert response.status_code == 200

    def test_post(self, client, member, send_webpush_mock):
        response = client.post(
            reverse("posts:create"), {"title": "test", "description": "test"}
        )
        MembershipFactory(community=member.community, role=Membership.Role.MODERATOR)

        post = Post.objects.get()
        assert response.url == post.get_absolute_url()
        assert post.owner == member.member
        assert post.community == member.community
        assert post.published

    def test_post_private(self, client, member, send_webpush_mock):

        MembershipFactory(community=member.community, role=Membership.Role.MODERATOR)

        response = client.post(
            reverse("posts:create"),
            {"title": "test", "description": "test", "save_private": "true"},
        )
        post = Post.objects.get()
        assert response.url == post.get_absolute_url()
        assert post.owner == member.member
        assert post.community == member.community
        assert not post.published

    def test_post_private_path(self, client, member, send_webpush_mock):

        MembershipFactory(community=member.community, role=Membership.Role.MODERATOR)

        response = client.post(
            reverse("posts:create_private"), {"title": "test", "description": "test"},
        )
        post = Post.objects.get()
        assert response.url == post.get_absolute_url()
        assert post.owner == member.member
        assert post.community == member.community
        assert not post.published


class TestPostUpdateView:
    def test_get(self, client, post_for_member):
        response = client.get(reverse("posts:update", args=[post_for_member.id]))
        assert response.status_code == 200

    def test_post(self, client, post_for_member, send_webpush_mock):
        response = client.post(
            reverse("posts:update", args=[post_for_member.id]),
            {"title": "UPDATED", "description": post_for_member.description},
        )
        post_for_member.refresh_from_db()
        assert response.url == post_for_member.get_absolute_url()
        assert post_for_member.title == "UPDATED"
        assert post_for_member.editor == post_for_member.owner
        assert post_for_member.edited

    def test_post_with_reshare(self, client, post_for_member, send_webpush_mock):

        reshare = post_for_member.reshare(UserFactory())

        client.post(
            reverse("posts:update", args=[post_for_member.id]),
            {"title": "UPDATED", "description": post_for_member.description},
        )

        post_for_member.refresh_from_db()
        reshare.refresh_from_db()
        assert post_for_member.title == "UPDATED"
        assert reshare.title == "UPDATED"

    def test_post_private(self, client, member, send_webpush_mock):
        post = PostFactory(
            owner=member.member, community=member.community, published=None
        )
        response = client.post(
            reverse("posts:update", args=[post.id]),
            {"title": "UPDATED", "description": post.description},
        )
        post.refresh_from_db()
        assert response.url == post.get_absolute_url()
        assert post.title == "UPDATED"
        assert post.published is None


class TestPostUpdateTagsView:
    def test_get(self, client, moderator, post):
        response = client.get(reverse("posts:update_tags", args=[post.id]))
        assert response.status_code == 200

    def test_post(self, client, moderator, post, mailoutbox, send_webpush_mock):
        response = client.post(
            reverse("posts:update_tags", args=[post.id]), {"hashtags": "#update"},
        )
        post.refresh_from_db()
        assert response.url == post.get_absolute_url()
        assert post.hashtags == "#update"
        assert post.editor == moderator.member
        assert post.edited

        notification = Notification.objects.first()
        assert notification.recipient == post.owner
        assert notification.actor == moderator.member
        assert notification.verb == "edit"

        assert mailoutbox[0].to == [post.owner.email]
        assert send_webpush_mock.is_called()


class TestPostCommentCreateView:
    def test_get(self, client, member):
        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.get(reverse("posts:comment", args=[post.id]))
        assert response.status_code == 200

    def test_post(self, client, member, send_webpush_mock):
        owner = UserFactory()
        MembershipFactory(member=owner, community=member.community)
        post = PostFactory(community=member.community, owner=owner)
        response = client.post(
            reverse("posts:comment", args=[post.id]),
            {"content": "test"},
            HTTP_HOST=member.community.domain,
        )
        comment = Comment.objects.get()
        assert response.url == comment.get_absolute_url()
        assert comment.owner == member.member
        assert comment.content_object == post

        notification = Notification.objects.get(recipient=post.owner, comment=comment)
        assert notification.verb == "new_comment"


class TestPostDeleteView:
    def test_get(self, client, post_for_member):
        # test confirmation page for non-JS clients
        response = client.get(reverse("posts:delete", args=[post_for_member.id]))
        assert response.status_code == 200

    def test_post(self, client, post_for_member):
        response = client.post(reverse("posts:delete", args=[post_for_member.id]))
        assert response.url == settings.LOCALHUB_HOME_PAGE_URL
        assert Post.objects.count() == 0

    def test_post_if_private(self, client, member):
        post = PostFactory(
            owner=member.member, community=member.community, published=None
        )
        response = client.post(reverse("posts:delete", args=[post.id]))
        assert response.url == reverse("activities:private")
        assert Post.objects.count() == 0

    def test_post_by_moderator(self, client, moderator, mailoutbox, send_webpush_mock):
        post = PostFactory(
            community=moderator.community,
            owner=MembershipFactory(community=moderator.community).member,
        )
        response = client.post(reverse("posts:delete", args=[post.id]))
        assert response.url == settings.LOCALHUB_HOME_PAGE_URL
        assert Post.objects.deleted().count() == 1

        assert send_webpush_mock.delay.called
        assert mailoutbox[0].to == [post.owner.email]


class TestPostDetailView:
    def test_get(self, client, post, member):

        notification = NotificationFactory(
            recipient=member.member, content_object=post, is_read=False
        )
        response = client.get(post.get_absolute_url(), HTTP_HOST=post.community.domain)
        assert response.status_code == 200
        assert "comment_form" in response.context
        notification.refresh_from_db()
        assert notification.is_read


class TestPostReshareView:
    def test_post(self, client, member, send_webpush_mock):

        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(
                community=member.community, member=UserFactory(),
            ).member,
        )
        response = client.post(
            reverse("posts:reshare", args=[post.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.url == post.reshares.first().get_absolute_url()
        assert post.reshares.filter(owner=member.member).count() == 1
        assert (
            Notification.objects.filter(
                actor=member.member, recipient=post.owner, verb="reshare"
            ).count()
            == 1
        )


class TestPostPinView:
    def test_post(self, client, moderator):

        # any pinned activities should be un-pinned
        already_pinned = PostFactory(
            community=moderator.community, owner=moderator.member, is_pinned=True
        )

        post = PostFactory(
            community=moderator.community,
            owner=MembershipFactory(community=moderator.community).member,
        )
        response = client.post(reverse("posts:pin", args=[post.id]),)
        assert response.url == settings.LOCALHUB_HOME_PAGE_URL

        already_pinned.refresh_from_db()
        post.refresh_from_db()

        assert post.is_pinned
        assert not already_pinned.is_pinned


class TestPostUnpinView:
    def test_post(self, client, moderator):

        post = PostFactory(
            community=moderator.community,
            owner=MembershipFactory(community=moderator.community).member,
            is_pinned=True,
        )
        response = client.post(reverse("posts:unpin", args=[post.id]))
        assert response.url == settings.LOCALHUB_HOME_PAGE_URL

        post.refresh_from_db()
        assert not post.is_pinned


class TestPublishView:
    def test_post(self, client, member, mailoutbox, send_webpush_mock):
        post = PostFactory(
            owner=member.member, community=member.community, published=None
        )
        response = client.post(reverse("posts:publish", args=[post.id]))
        assert response.url == post.get_absolute_url()
        post.refresh_from_db()
        assert post.published


class TestPostBookmarkView:
    def test_post(self, client, member):
        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.post(reverse("posts:bookmark", args=[post.id]),)
        assert response.status_code == 200
        bookmark = Bookmark.objects.get()
        assert bookmark.user == member.member


class TestPostRemoveBookmarkView:
    def test_post(self, client, member):
        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        BookmarkFactory(
            user=member.member, content_object=post, community=post.community,
        )
        response = client.post(reverse("posts:remove_bookmark", args=[post.id]),)
        assert response.status_code == 200
        assert Bookmark.objects.count() == 0


class TestPostLikeView:
    def test_post(self, client, member, send_webpush_mock):
        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.post(reverse("posts:like", args=[post.id]),)
        assert response.status_code == 200
        like = Like.objects.get()
        assert like.user == member.member


class TestPostDislikeView:
    def test_post(self, client, member):
        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        LikeFactory(
            user=member.member,
            content_object=post,
            community=post.community,
            recipient=post.owner,
        )
        response = client.post(reverse("posts:dislike", args=[post.id]),)
        assert response.status_code == 200
        assert Like.objects.count() == 0


class TestFlagView:
    def test_get(self, client, member):
        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.get(reverse("posts:flag", args=[post.id]))
        assert response.status_code == 200

    def test_post(self, client, member, send_webpush_mock):
        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        moderator = MembershipFactory(
            community=post.community,
            role=Membership.Role.MODERATOR,
            member=UserFactory(),
        )
        response = client.post(
            reverse("posts:flag", args=[post.id]), data={"reason": "spam"}
        )
        assert response.url == post.get_absolute_url()

        flag = Flag.objects.get()
        assert flag.user == member.member

        notification = Notification.objects.get()
        assert notification.recipient == moderator.member


class TestOpengraphPreviewView:
    def test_get(self, client, mock_url_resolver, mock_html_scraper_from_url):
        response = client.get(
            reverse("posts:opengraph_preview"), {"url": "https://imgur.com"}
        )
        assert response.status_code == 200
        data = response.json()["fields"]
        assert data["title"] == "Imgur"
        assert data["url"] == "https://imgur.com/"
        assert data["opengraph_image"] == "https://imgur.com/cat.gif"
        assert data["opengraph_description"] == "cat"

    def test_get_if_image(self, client, mock_url_image_resolver):
        response = client.get(
            reverse("posts:opengraph_preview"), {"url": "https://imgur.com/cat.gif"}
        )
        assert response.status_code == 200
        data = response.json()["fields"]
        assert data["title"] == "cat.gif"
        assert data["url"] == "https://imgur.com/cat.gif"
        assert data["opengraph_image"] == "https://imgur.com/cat.gif"
        assert data["opengraph_description"] == ""

    def test_get_bad_result(self, client, mock_html_scraper_from_invalid_url):
        response = client.get(
            reverse("posts:opengraph_preview"), {"url": "https://imgur.com"}
        )
        assert response.status_code == 400
