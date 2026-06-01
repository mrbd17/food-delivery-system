from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.Restaurant)
admin.site.register(models.MenuItem)
admin.site.register(models.Category)
