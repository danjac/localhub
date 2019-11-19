# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from ..decorators import with_cached_context_value


class TestWithCachedContextValue:
    def test_is_cached_in_context(self):
        @with_cached_context_value
        def some_random_func(context):
            return 200

        context = {
            "_some_random_func_cached": 100,
        }

        assert some_random_func(context) == 100

    def test_is_not_cached_in_context(self):
        @with_cached_context_value
        def some_random_func(context):
            return 200

        context = {}

        assert some_random_func(context) == 200
        assert context["_some_random_func_cached"] == 200
