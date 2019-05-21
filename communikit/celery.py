# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "communikit.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

# https://django-configurations.readthedocs.io/en/stable/cookbook/#celery

import configurations  # noqa

configurations.setup()

app = Celery("communikit")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request}")
