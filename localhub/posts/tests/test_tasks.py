# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import factory
import pytest

from django.db.models import signals


from pytest_mock import MockFixture

from localhub.posts import tasks
from localhub.posts.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestFetchTitleFromUrl:
    @factory.django.mute_signals(signals.post_save)
    def test_no_title_and_url(self, mocker: MockFixture):
        # should insert a title from the URL
        mocker.patch(
            "localhub.posts.tasks.fetch_title_from_url",
            return_value="Google",
        )
        post = PostFactory(title="", url="http://google.com")
        tasks.fetch_post_title_from_url(post.id)

        post.refresh_from_db()
        assert post.title == "Google"

    @factory.django.mute_signals(signals.post_save)
    def test_title_no_url(self):
        # should do nothing
        post = PostFactory(title="testme", url="")
        tasks.fetch_post_title_from_url(post.id)

        post.refresh_from_db()
        assert post.title == "testme"

    @factory.django.mute_signals(signals.post_save)
    def test_title_and_url(self):
        # should do nothing
        post = PostFactory(title="testme", url="http://google.com")
        tasks.fetch_post_title_from_url(post.id)

        post.refresh_from_db()
        assert post.title == "testme"

    @factory.django.mute_signals(signals.post_save)
    def test_fetch_title_fails(self, mocker: MockFixture):
        # should insert domain
        mocker.patch(
            "localhub.posts.tasks.fetch_title_from_url", return_value=None
        )
        post = PostFactory(title="", url="http://google.com")
        tasks.fetch_post_title_from_url(post.id)

        post.refresh_from_db()
        assert post.title == "google.com"
