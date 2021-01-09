# Standard Library
from functools import partial

# Django
from django.contrib import messages

# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


def create_header_message(response, msg_type, msg):
    response["X-Message"] = msg
    response["X-Message-Type"] = msg_type


debug_header_message = partial(create_header_message, msg_type=messages.DEBUG)
error_header_message = partial(create_header_message, msg_type=messages.ERROR)
info_header_message = partial(create_header_message, msg_type=messages.INFO)
success_header_message = partial(create_header_message, msg_type=messages.SUCCESS)
warning_header_message = partial(create_header_message, msg_type=messages.WARNING)
