from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.menu.models import MenuItem

from .models import Cart, CartItem


def get_or_create_active_cart(user=None, guest_id=None):
    if not user and not guest_id:
        raise ValueError(" user or guest_Id is required ")

    lookup = {"is_active": True}

    if user:
        lookup["user"] = user
    else:
        lookup["guest_id"] = guest_id

    cart, _ = Cart.objects.get_or_create(**lookup)

    return cart


@transaction.atomic
def add_to_cart(product_id, user=None, guest_id=None):

    cart = get_or_create_active_cart(user=user, guest_id=guest_id)

    product = get_object_or_404(MenuItem, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        menu_item=product,
        defaults={"price_snapshot": product.price, "quantity": 1},
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save(update_fields=["quantity"])

    return cart_item


@transaction.atomic
def update_cart_item(item_id, quantity, user=None, guest_id=None):

    cart = get_or_create_active_cart(user=user, guest_id=guest_id)

    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if quantity == 0:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.save(update_fields=["quantity"])

    return cart_item


@transaction.atomic
def remove_cart_item(item_id, user=None, guest_id=None):

    cart = get_or_create_active_cart(user=user, guest_id=guest_id)

    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    cart_item.delete()


@transaction.atomic
def clear_cart(user=None, guest_id=None):

    cart = get_or_create_active_cart(user=user, guest_id=guest_id)
    cart.clear()
