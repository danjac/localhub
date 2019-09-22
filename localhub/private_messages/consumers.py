# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group.add(
                self.scope["user"].username, self.channel_name
            )
            await self.accept()

    async def disconnect(self):
        await self.channel_layer.group.discard(
            self.scope["user"].username, self.channel_name
        )

    async def receive(self, data):
        await self.send(text_data=json.dumps(data))
