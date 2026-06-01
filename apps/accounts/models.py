import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here.


class Profile(models.Model):

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("restaurant", "Restaurant"),
        ("customer", "Customer"),
        ("delivery", "Delivery"),
    ]
    theme_choices = [("light", "Light"), ("dark", "Dark")]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")
    avatar = models.ImageField(
        null=True, blank=True, default="avatars/user.jpg", upload_to="avatars/"
    )
    theme = models.CharField(max_length=20, choices=theme_choices, default="light")
    phone = models.CharField(max_length=25, default="")
    address = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    purpose = models.CharField(
        max_length=20, choices=[("verify", "Verify Email"), ("reset", "Reset Pessword")]
    )

    def is_expired(self):
        return timezone.now() > self.expires_at
