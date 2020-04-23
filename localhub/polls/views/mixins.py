# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


class PollQuerySetMixin:
    def get_queryset(self):
        return super().get_queryset().with_answers()
