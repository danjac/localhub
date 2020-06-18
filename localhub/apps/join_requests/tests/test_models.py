# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Localhub
from localhub.apps.communities.factories import MembershipFactory
from localhub.apps.users.factories import UserFactory

# Local
from ..factories import JoinRequestFactory
from ..models import JoinRequest

pytestmark = pytest.mark.django_db


class TestJoinRequestManager:
    def test_search(self, transactional_db):
        user = UserFactory(name="Tester")
        req = JoinRequestFactory(sender=user)
        assert JoinRequest.objects.search("tester").first() == req

    def test_for_sender(self, join_request):
        assert JoinRequest.objects.for_sender(join_request.sender).exists()

    def test_for_sender_if_member(self, join_request):
        MembershipFactory(community=join_request.community, member=join_request.sender)
        assert not JoinRequest.objects.for_sender(join_request.sender).exists()

    def test_pending(self):
        JoinRequestFactory(status=JoinRequest.Status.PENDING)
        assert JoinRequest.objects.pending().exists()

    def test_accepted(self):
        JoinRequestFactory(status=JoinRequest.Status.ACCEPTED)
        assert JoinRequest.objects.accepted().exists()

    def test_rejected(self):
        JoinRequestFactory(status=JoinRequest.Status.REJECTED)
        assert JoinRequest.objects.rejected().exists()

    def test_for_community(self, join_request):
        assert JoinRequest.objects.for_community(join_request.community).exists()


class TestJoinRequest:
    def test_is_pending(self):
        assert JoinRequest(status=JoinRequest.Status.PENDING).is_pending()

    def test_is_accepted(self):
        assert JoinRequest(status=JoinRequest.Status.ACCEPTED).is_accepted()

    def test_is_rejected(self):
        assert JoinRequest(status=JoinRequest.Status.REJECTED).is_rejected()
