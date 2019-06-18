from django.conf import settings


def user_display(user: settings.AUTH_USER_MODEL) -> str:
    return user.name or user.username
