from localhub.conversations.models import Message


class TestMessageModel:
    def test_get_abbreviation(self):

        msg = Message(message="Hello\nthis is a *test*")
        assert msg.get_abbreviation() == "Hello this is a test"
