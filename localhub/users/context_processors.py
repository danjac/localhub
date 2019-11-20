# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


def user_preferences(request):
    return {"darkmode": request.COOKIES.get("darkmode") == "true"}
