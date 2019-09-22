# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add(
                self.scope["user"].username, self.channel_name
            )
            await self.accept()

    async def disconnect(self):
        await self.channel_layer.group_discard(
            self.scope["user"].username, self.channel_name
        )

    # TBD: the Message instance itself is generated in db by AJAX action.
    # we just pass the text_data here as is (await self.send(....))
    # payload includes message_id
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # Send message to room group
        await self.channel_layer.group_send(
            self.scope["user"].username,
            {"type": "send_message", "message": message},
        )

    async def send_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
