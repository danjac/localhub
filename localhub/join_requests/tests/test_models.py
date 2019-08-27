import pytest


from localhub.join_requests.tests.factories import JoinRequestFactory

pytestmark = pytest.mark.django_db


class TestJoinRequestModel:
    def test_get_sender_if_sender_id(self):
        join_request = JoinRequestFactory()
        assert join_request.get_sender()

    def test_get_sender_if_email_exists(self, user):
        join_request = JoinRequestFactory(email=user.email, sender=None)
        assert join_request.get_sender() == user

    def test_get_sender_if_email_not_exists(self):
        join_request = JoinRequestFactory(sender=None)
        assert join_request.get_sender() is None
