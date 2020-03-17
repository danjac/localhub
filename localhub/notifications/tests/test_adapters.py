# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.posts.notifications import PostAdapter


pytestmark = pytest.mark.django_db


@pytest.fixture()
def adapter(notification):
    return PostAdapter(notification)


class TestAdapter:
    def test_render_to_template(self, adapter):
        response = adapter.render_to_template()
        assert "has mentioned you" in response
        assert "post" in response

    def test_send_notification(self, adapter, mailoutbox, send_webpush_mock):
        adapter.send_notification()
        assert send_webpush_mock.is_called
        assert len(mailoutbox) == 1

    def test_webpusher_send(self, adapter, send_webpush_mock):
        adapter.webpusher.send()
        assert send_webpush_mock.is_called

    def test_mailer_send(self, adapter, mailoutbox):
        adapter.mailer.send()
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [adapter.notification.recipient.email]
