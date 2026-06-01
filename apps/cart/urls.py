

import uuid

from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_cart_api, name="cart"),
    path("add/", views.AddToCartApi, name="cart_add"),
    path("update/", views.UpdateCartItemAPI, name="cart_update_item"),
    path("remove/", views.RemoveCartItemAPI, name="cart_remove_item"),
]
