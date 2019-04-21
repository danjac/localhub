from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    name = models.CharField(_("Full name of user"), blank=True, max_length=255)
