from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    name = models.CharField(_("Full name of user"), blank=True, max_length=255)

    def get_profile_url(self) -> str:
        """
        Link to (public) profile content page
        """
        return reverse("content:profile", args=[self.username])
