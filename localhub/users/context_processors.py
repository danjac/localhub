# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


def theme(request):
    return {"theme": request.COOKIES.get('theme', 'light')}
