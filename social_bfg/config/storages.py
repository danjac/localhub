# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Custom Django S3 storage backends for media and static.

These allow both media and storage to use the same S3
bucket safely with different sub-locations.
"""

# Django
from django.conf import settings
from django.contrib.staticfiles.storage import ManifestFilesMixin

# Third Party Libraries
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    location = settings.AWS_MEDIA_LOCATION
    file_overwrite = False


class StaticStorage(ManifestFilesMixin, S3Boto3Storage):
    location = settings.AWS_STATIC_LOCATION

    def read_manifest(self):
        # handle s3 missing file issue
        try:
            with self.open(self.manifest_name) as manifest:
                return manifest.read().decode()
        except (FileNotFoundError, IOError):
            return None
