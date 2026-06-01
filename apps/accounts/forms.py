import random

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    username = forms.CharField(required=False)  # optional input

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("username"):
            base_username = f"{cleaned_data.get('first_name','')}{cleaned_data.get('last_name','')}".lower()
            username = base_username
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{random.randint(1000,9999)}"
            cleaned_data["username"] = username

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["username"]
        user.is_active = False
        if commit:
            user.save()
        return user
