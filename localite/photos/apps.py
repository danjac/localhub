# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.apps import AppConfig


class PhotosConfig(AppConfig):
    name = "localite.photos"

    def ready(self):
        import localite.photos.signals # noqa
