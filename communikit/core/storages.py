# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from storages.backends.s3boto3 import S3Boto3Storage

from . import app_settings


class MediaStorage(S3Boto3Storage):
    location = app_settings.AWS_MEDIA_LOCATION
    file_overwrite = False


class StaticStorage(S3Boto3Storage):
    location = app_settings.AWS_STATIC_LOCATION
