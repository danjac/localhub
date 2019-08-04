# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Any, Optional


def nested_getattr(obj: Any, attr: str, default: Optional[Any] = None) -> Any:
    """
    Returns value from dot-separated nested attributes.

    Example:

    class NestedClass:
        a = "1"

    class SomeClass:
        nested = NestedClass()

    s = SomeClass()
    result = nested_getattr(s, "nested.a")
    assert result == "1"
    """
    for a in attr.split("."):
        try:
            obj = getattr(obj, a)
        except AttributeError:
            if default:
                return default
            raise
    return obj
