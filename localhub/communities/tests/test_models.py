# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.test import override_settings

from localhub.join_requests.models import JoinRequest
from localhub.users.factories import UserFactory

from ..factories import CommunityFactory, MembershipFactory
from ..models import Community, Membership

pytestmark = pytest.mark.django_db


class TestCommunityManager:
    def test_with_num_members(self):
        MembershipFactory()
        community = Community.objects.with_num_members().first()
        assert community.num_members == 1

    def test_with_is_member_if_member(self):
        community = CommunityFactory()
        member = MembershipFactory(community=community).member
        first = Community.objects.with_is_member(member).first()
        assert first.is_member
        assert first.member_role == Membership.Role.MEMBER

    def test_with_is_member_if_not_member(self):
        CommunityFactory()
        user = UserFactory()
        first = Community.objects.with_is_member(user).first()
        assert not first.is_member
        assert first.member_role is None

    def test_with_is_member_if_anonymous(self):
        CommunityFactory()
        user = AnonymousUser()
        first = Community.objects.with_is_member(user).first()
        assert not first.is_member
        assert first.member_role is None

    def test_accessible_if_public(self, user):
        CommunityFactory(public=True)
        assert Community.objects.accessible(user).exists()

    def test_accessible_if_not_public_and_member(self):
        community = CommunityFactory(public=False)
        user = MembershipFactory(community=community).member
        assert Community.objects.accessible(user).exists()

    def test_accessible_if_not_public_and_not_member(self, user):
        CommunityFactory(public=False)
        assert not Community.objects.accessible(user).exists()

    def test_get_current_if_community_on_site(self, rf):

        req = rf.get("/", HTTP_HOST="example.com")
        community = CommunityFactory(domain="example.com")
        assert Community.objects.get_current(req) == community

    def test_get_current_with_port(self, rf):
        req = rf.get("/", HTTP_HOST="example.com:8000")
        community = CommunityFactory(domain="example.com:8000")
        assert Community.objects.get_current(req) == community

    def test_get_current_if_inactive_community_on_site(self, rf):
        req = rf.get("/", HTTP_HOST="example.com")
        CommunityFactory(domain="example.com", active=False)
        assert Community.objects.get_current(req).id is None

    def test_get_current_if_no_community_available(self, rf):
        req = rf.get("/", HTTP_HOST="example.com")
        assert Community.objects.get_current(req).id is None


class TestCommunityModel:
    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_get_absolute_url_if_debug(self):
        community = Community(domain="testing.com")
        assert community.get_absolute_url() == "http://testing.com"

    @override_settings(SECURE_SSL_REDIRECT=True)
    def test_get_absolute_url_if_production(self):
        community = Community(domain="testing.com")
        assert community.get_absolute_url() == "https://testing.com"

    def test_is_email_blacklisted_if_ok(self):
        community = Community()
        assert not community.is_email_blacklisted("tester@gmail.com")

    def test_is_email_blacklisted_if_domain_blacklisted(self):
        community = Community(blacklisted_email_domains="gmail.com")
        assert community.is_email_blacklisted("tester@gmail.com")
        assert community.is_email_blacklisted("tester2@gmail.com")

    def test_is_email_blacklisted_if_address_blacklisted(self):
        community = Community(blacklisted_email_addresses="tester@gmail.com")
        assert community.is_email_blacklisted("tester@gmail.com")
        assert not community.is_email_blacklisted("tester2@gmail.com")

    def test_get_members(self, member):
        assert member.community.get_members().first() == member.member

    def test_get_moderators(self, moderator: Membership):
        assert moderator.community.get_moderators().first() == moderator.member

    def test_get_admins(self, admin: Membership):
        assert admin.community.get_admins().first() == admin.member

    def test_get_email_domain_if_none_set(self):

        community = CommunityFactory()
        assert community.get_email_domain() == community.domain

    def test_get_email_domain_if_set(self):

        community = CommunityFactory(email_domain="gmail.com")
        assert community.get_email_domain() == "gmail.com"

    def test_resolve_email(self):
        community = CommunityFactory(email_domain="gmail.com")
        assert community.resolve_email("no-reply") == "no-reply@gmail.com"

    def test_get_content_warning_tags(self):
        community = Community(content_warning_tags="#nsfw #politics")
        assert community.get_content_warning_tags() == {"nsfw", "politics"}

    def test_invalid_domain_name(self):

        community = Community(name="test", domain="testing")
        with pytest.raises(ValidationError):
            community.clean_fields()


class TestMembershipModel:
    def test_join_requests_deleted(self, member, transactional_db):
        JoinRequest.objects.create(sender=member.member, community=member.community)
        member.delete()
        assert not JoinRequest.objects.exists()
