import uuid

from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL
# Create your models here.


class Restaurant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to="restaurant_logos/", blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    CATEGORY_CHOICES = [
        ("drinks", "Drinks"),
        ("main", "Main Meals"),
        ("desserts", "Desserts"),
        ("snacks", "Snacks"),
        ("salads", "Salads"),
    ]
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="categories"
    )

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="menu_items"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    img = models.ImageField(upload_to="menu_images/", null=True, blank=True)
    is_menu = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.category.name}"
