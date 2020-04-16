# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from vanilla import GenericModelView

from .success import SuccessMixin


class BaseActionView(SuccessMixin, GenericModelView):
    """Base class for simple AJAX action views (usually POST) with
    standard success response. Automatically loads object at setup
    """

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.object = self.get_object()
