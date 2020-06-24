# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Local
from . import env

DEFAULT_FILE_STORAGE = "localhub.config.storages.MediaStorage"
STATICFILES_STORAGE = "localhub.config.storages.StaticStorage"

AWS_MEDIA_LOCATION = "media"
AWS_STATIC_LOCATION = "static"

AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = env.str("AWS_S3_CUSTOM_DOMAIN", default=None)
AWS_S3_REGION_NAME = env.str("AWS_S3_REGION_NAME", default="eu-north-1")

AWS_QUERYSTRING_AUTH = False
AWS_IS_GZIPPED = True
AWS_DEFAULT_ACL = "public-read"

AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=600"}
