from decimal import Decimal

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.cart.models import Cart

from .models import Address, Order, OrderItem
from .tasks import send_order_confirmation_email


def notify_update_status(order):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"order_{order.id}",
        {
            "type": "order_update",
            "order_id": str(order.id),
            "status": order.status,
            "status_display": order.get_status_display(),
            "updated_at": order.updated_at.isoformat(),
        },
    )


@transaction.atomic
def create_order(user, payment_method, delivery_address_id):
    cart = Cart.objects.prefetch_related("items__menu_item").get(user=user)

    if not cart.items.exists():
        raise ValueError(
            "Your Cart Is Empyt Can't create order untill you add something to the cart"
        )

    address = get_object_or_404(Address, id=delivery_address_id, user=user)

    subtotal = cart.subtotal
    tax = subtotal * Decimal("0.08")
    total = subtotal + tax

    order = Order.objects.create(
        user=user,
        payment_method=payment_method,
        delivery_address=address,
        tax=tax,
        total=total,
    )

    order_items = []
    items = cart.items.all()

    for item in items:
        order_items.append(
            OrderItem(
                order=order,
                menu_item=item.menu_item,
                name=item.menu_item.name,
                quantity=item.quantity,
                price=item.price_snapshot,
            )
        )

    OrderItem.objects.bulk_create(order_items)
    cart.clear()
    transaction.on_commit(lambda: send_order_confirmation_email.delay(order.id))
    return order


ALLOWED_TRANSACTIONS = {
    "PENDING": ["CONFIRMED", "CANCELED"],
    "CONFIRMED": ["CANCELED", "PREPARING"],
    "PREPARING": ["DELIVERED"],
    "DELIVERED": [],
    "CANCELED": [],
}


def update_order_status(user, order_id, new_status):

    order = get_object_or_404(Order, id=order_id, user=user)

    allowed = ALLOWED_TRANSACTIONS.get(order.status, [])

    if new_status not in allowed:
        raise ValueError(f"you can't change status from {order.status} to {new_status}")

    order.status = new_status
    order.save(update_fields=["status"])
    notify_update_status(order)
    return order


def cancel_order(user, order_id):

    order = get_object_or_404(Order, id=order_id)

    if order.user != user:
        raise PermissionDenied("You can't change this order")

    allowed = ALLOWED_TRANSACTIONS.get(order.status, [])
    print(allowed)
    # if "CANCELED" not in allowed:
    #     raise ValueError("This order can't be cancelled")

    order.status = "CANCELED"
    order.save(update_fields=["status"])
    notify_update_status(order)

    return order
