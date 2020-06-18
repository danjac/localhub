# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import os

# Third Party Libraries
import configurations  # noqa
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "localhub.config.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

# https://django-configurations.readthedocs.io/en/stable/cookbook/#celery


configurations.setup()

app = Celery("localhub")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request}")
