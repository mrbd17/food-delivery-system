import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Order


class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("connected hit")
        self.user = self.scope["user"]

        if not self.user:
            await self.close(code=4001)
            return

        self.order_id = self.scope["url_route"]["kwargs"].get("order_id")
        if not self.order_id:
            await self.close(code=4002)
            return

        if not await self.can_access_order(self.user, self.order_id):
            await self.close(code=4001)
            return

        order = await self.get_order_data(self.order_id, self.user)

        if not order:
            await self.close(4004)
            return

        self.group_name = f"order_{self.order_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

        await self.send(
            text_data=json.dumps(
                {
                    "type": "connection_established",
                    "order": {
                        "id": str(order.id),
                        "status": order.status,
                        "status_display": order.get_status_display(),
                    },
                }
            )
        )

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

        except Exception:
            return

        if data.get("type") == "ping":
            await self.send(text_data=json.dumps({"type": "pong"}))

    async def order_update(self, event):
        print("consumer event received")
        await self.send(
            text_data=json.dumps(
                {
                    "type": "order.updated",
                    "order_id": event["order_id"],
                    "status": event["status"],
                    "status_display": event["status_display"],
                    "updated_at": event["updated_at"],
                }
            )
        )

    @database_sync_to_async
    def can_access_order(self, user, order_id):
        return Order.objects.filter(id=order_id, user=user).exists()

    @database_sync_to_async
    def get_order_data(self, order_id, user):
        order = Order.objects.filter(id=order_id, user=user).first()

        if not order:
            return None
        else:
            return order
