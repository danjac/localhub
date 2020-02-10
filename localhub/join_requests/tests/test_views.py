# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.urls import reverse

from localhub.communities.models import Membership
from localhub.users.factories import UserFactory

from ..factories import JoinRequestFactory
from ..models import JoinRequest

pytestmark = pytest.mark.django_db


class TestJoinRequestListView:
    def test_get(self, client, admin):
        JoinRequestFactory.create_batch(3, community=admin.community)
        response = client.get(reverse("join_requests:list"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 3


class TestJoinRequestDetailView:
    def test_get(self, client, admin):
        join_request = JoinRequestFactory(community=admin.community)
        response = client.get(join_request.get_absolute_url())
        assert response.status_code == 200


class TestJoinRequestDeleteView:
    def test_get(self, client, admin):
        join_request = JoinRequestFactory(community=admin.community)
        response = client.get(reverse("join_requests:delete", args=[join_request.id]))
        assert response.status_code == 200

    def test_post(self, client, admin):
        join_request = JoinRequestFactory(community=admin.community)
        response = client.post(reverse("join_requests:delete", args=[join_request.id]))
        assert response.url == reverse("join_requests:list")
        assert JoinRequest.objects.count() == 0


class TestJoinRequestCreateView:
    def test_get(self, client, login_user, community):
        assert client.get(reverse("join_requests:create")).status_code == 200

    def test_post(self, client, mailoutbox, login_user, community):

        admin = UserFactory()
        Membership.objects.create(
            community=community, member=admin, role=Membership.ROLES.admin
        )
        response = client.post(reverse("join_requests:create"))
        assert response.url == reverse("community_welcome")
        join_request = JoinRequest.objects.get()
        assert join_request.sender == login_user
        assert join_request.community == community
        mail = mailoutbox[0]
        assert mail.to == [admin.email]


class TestJoinRequestAcceptView:
    def test_post(self, client, mailoutbox, admin, send_notification_webpush_mock):
        admin.member.notification_preferences = ["new_member"]
        admin.member.save()
        join_request = JoinRequestFactory(community=admin.community)
        response = client.post(reverse("join_requests:accept", args=[join_request.id]))
        assert response.url == reverse("join_requests:list")
        join_request.refresh_from_db()
        assert join_request.is_accepted()
        assert Membership.objects.filter(
            member=join_request.sender, community=admin.community
        ).exists()
        mail = mailoutbox[0]
        assert mail.to == [join_request.sender.email]
        other_member_mail = mailoutbox[1]
        assert other_member_mail.to == [admin.member.email]


class TestJoinRequestRejectView:
    def test_post(self, client, mailoutbox, admin):
        join_request = JoinRequestFactory(community=admin.community)
        response = client.post(reverse("join_requests:reject", args=[join_request.id]))
        assert response.url == reverse("join_requests:list")
        join_request.refresh_from_db()
        assert join_request.is_rejected()
        assert not Membership.objects.filter(
            member=join_request.sender, community=admin.community
        ).exists()
        mail = mailoutbox[0]
        assert mail.to == [join_request.sender.email]
