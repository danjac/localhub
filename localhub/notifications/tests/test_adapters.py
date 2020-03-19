# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.posts.notifications import PostAdapter

from ..adapters import DefaultAdapter

pytestmark = pytest.mark.django_db


@pytest.fixture()
def adapter(notification):
    return PostAdapter(notification)


@pytest.fixture()
def empty_adapter(notification):
    return DefaultAdapter(notification)


class TestAdapter:
    def test_render_to_tag(self, adapter):
        response = adapter.render_to_tag()
        assert "has mentioned you" in response
        assert "post" in response

    def test_render_to_tag_if_not_allowed_verb(self, empty_adapter):
        assert empty_adapter.render_to_tag() == ""

    def test_send_notification(self, adapter, mailoutbox, send_webpush_mock):
        adapter.send_notification()
        assert send_webpush_mock.delay.called
        assert len(mailoutbox) == 1

    def test_send_notification_if_not_allowed_verb(
        self, empty_adapter, mailoutbox, send_webpush_mock
    ):
        empty_adapter.send_notification()
        assert not send_webpush_mock.delay.called
        assert len(mailoutbox) == 0

    def test_webpusher_send(self, adapter, send_webpush_mock):
        adapter.webpusher.send()
        assert send_webpush_mock.delay.called

    def test_mailer_send(self, adapter, mailoutbox):
        adapter.mailer.send()
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [adapter.notification.recipient.email]
