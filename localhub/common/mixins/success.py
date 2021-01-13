# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Local
from ..utils.messages import success_header_message


class SuccessHeaderMixin:
    """Provides defaults for success message and redirect URL."""

    success_message = None

    def get_success_message(self, success_message=None):
        """Returns success message string. Interpolates
        object and model verbose name as "object" and "model"
        respectively.

        Args:
            success_message(str, optional): a message string. If not provided
                then class should define success_message attribute.
                (default: None)
            object (Model, optional): Django Model instance. If None then
                self.object is assumed. (default: None)
            model (Model class, optional). Django Model class. If None then
                either object (see above) or self.model are assumed. (default: None)

        Returns:
            str or None if no message defined
        """
        success_message = success_message or getattr(self, "success_message", None)
        if success_message is None:
            return None

        object = getattr(self, "object", None)
        model = object or getattr(self, "model", None)

        dct = {}

        if object:
            dct["object"] = object
        if model:
            dct["model"] = model._meta.verbose_name

        return success_message % dct

    def render_success_message(self, response):
        if success_message := self.get_success_message():
            success_header_message(response, success_message)
        return response
