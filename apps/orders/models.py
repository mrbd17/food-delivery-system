import uuid

from django.contrib.auth.models import User
from django.db import models
from django_countries.fields import CountryField

from apps.menu.models import MenuItem


def generate_order_number():
    return f"ORD-{uuid.uuid4().hex[:10].upper()}"


class Address(models.Model):
    TYPE_HOME = "Home"
    TYPE_WORK = "Work"
    TYPE_OTHER = "Other"
    TYPE_CHOICES = [(TYPE_HOME, "Home"), (TYPE_WORK, "Work"), (TYPE_OTHER, "Other")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_HOME)
    full_name = models.CharField(max_length=100, null=True)
    country = CountryField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    postcode = models.CharField(max_length=50)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"


class Order(models.Model):
    ORDER_STATUS = [
        ("Pending", "pending"),
        ("Accepted", "accepted"),
        ("Perparing", "perparing"),
        ("Ready", "ready"),
        ("Deliverid", "Deliverid"),
        ("Canceld", "canceld"),
    ]

    PYMENT_METHOD = [("Cash", "cash"), ("Card", "card")]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(
        max_length=20, unique=True, default=generate_order_number
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order")
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=50, choices=ORDER_STATUS, default="Pending")
    payment_method = models.CharField(
        max_length=20, choices=PYMENT_METHOD, default="Card"
    )
    payment_status = models.CharField(max_length=100, default="pending")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"oreder #{self.created_at}"

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(
        MenuItem, on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.price * self.quantity
