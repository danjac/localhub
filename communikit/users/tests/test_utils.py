from django.contrib.auth import get_user_model

from communikit.users.utils import user_display


def test_user_display_with_name():
    user = get_user_model()(name="Test Person")
    assert user_display(user) == "Test Person"


def test_user_display_no_name():
    user = get_user_model()(username="tester")
    assert user_display(user) == "tester"
