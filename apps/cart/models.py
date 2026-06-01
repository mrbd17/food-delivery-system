import uuid

from django.contrib.auth.models import User
from django.db import models

from apps.menu.models import MenuItem

# Create your models here.


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cart", null=True, blank=True
    )
    guest_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "is_active"],
                condition=models.Q(is_active=True),
                name="unique_active_cart_per_user",
            ),
            models.UniqueConstraint(
                fields=["guest_id", "is_active"],
                condition=models.Q(is_active=True),
                name="unique_active_cart_per_guest",
            ),
        ]

    def __str__(self):
        return f"Cart {self.user or self.guest_id} - {self.id}"

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())

    def clear(self):
        return self.items.all().delete()


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    price_snapshot = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ("cart", "menu_item")

    @property
    def subtotal(self):
        return self.menu_item.price * self.quantity
