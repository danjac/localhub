# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

# from channels.security.websocket import AllowedHostsOriginValidator

from localhub.private_messages.routing import (
    urlpatterns as message_urlpatterns,
)


application = ProtocolTypeRouter(
    {"websocket": AuthMiddlewareStack(URLRouter(message_urlpatterns))}
)
