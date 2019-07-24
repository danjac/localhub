# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.core.exceptions import ValidationError
from django.test.client import RequestFactory

from localhub.communities.models import Community, Membership

from .factories import CommunityFactory

pytestmark = pytest.mark.django_db


class TestCommunityManager:
    def test_get_current_if_community_on_site(
        self, req_factory: RequestFactory
    ):

        req = req_factory.get("/", HTTP_HOST="example.com")
        community = CommunityFactory(domain="example.com")
        assert Community.objects.get_current(req) == community

    def test_get_current_with_port(self, req_factory: RequestFactory):

        req = req_factory.get("/", HTTP_HOST="example.com:8000")
        community = CommunityFactory(domain="example.com")
        assert Community.objects.get_current(req) == community

    def test_get_current_if_inactive_community_on_site(
        self, req_factory: RequestFactory
    ):
        req = req_factory.get("/", HTTP_HOST="example.com")
        CommunityFactory(domain="example.com", active=False)
        assert Community.objects.get_current(req).id is None

    def test_get_current_if_no_community_available(
        self, req_factory: RequestFactory
    ):
        req = req_factory.get("/", HTTP_HOST="example.com")
        assert Community.objects.get_current(req).id is None


class TestCommunityModel:
    def test_get_members(self, member: Membership):
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
        assert community.resolve_email("support") == "support@gmail.com"

    def test_get_content_warning_tags(self):
        community = Community(content_warning_tags="#nsfw #politics")
        assert community.get_content_warning_tags() == {"nsfw", "politics"}

    def test_invalid_domain_name(self):

        community = Community(name="test", domain="testing")
        with pytest.raises(ValidationError):
            community.clean_fields()
