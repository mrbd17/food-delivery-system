from django.contrib import admin

from accounts.models import EmailOTP, Profile

# Register your models here.

admin.site.register(Profile)
admin.site.register(EmailOTP)
