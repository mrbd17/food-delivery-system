from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from apps.menu.models import Category, MenuItem, Restaurant

from .models import Cart, CartItem


class TestCartApi(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="1234")
        self.restaurant = Restaurant.objects.create(name="Di-Da")
        self.category = Category.objects.create(
            name="Main Meals", restaurant=self.restaurant
        )
        self.product = MenuItem.objects.create(
            name="Bruger", price=100, category=self.category, restaurant=self.restaurant
        )
        self.cart = Cart.objects.create(user=self.user)
        self.item = CartItem.objects.create(
            menu_item=self.product, cart=self.cart, price_snapshot=self.product.price
        )
        self.url = "/api/v1/cart/add/"

    def test_add_to_cart_success(self):

        self.client.login(username="test", password="1234")

        data = {
            "product_id": self.product.id,
        }

        response = self.client.post(self.url, data)

        print("Status:", response.status_code)
        if hasattr(response, "data"):
            print("Data:", response.data)
        else:
            print("Data", response.content)

        self.assertEqual(response.status_code, 200)

    def test_update_cart_item(self):
        url = "/api/v1/cart/update/"

        self.client.login(username="test", password="1234")

        data = {"item_id": self.item.id, "quantity": -1}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        print("Status:", response.status_code)

        if hasattr(response, "data"):
            print("Data:", response.data)

        else:
            print("Data:", response.content)

    def test_remove_cart_item(self):
        self.client.login(username="test", password="1234")

        data = {
            "item_id": self.item.id,
        }

        response = self.client.delete("/api/cart/remove/", data)

        print("Status:", response.status_code)

        print("Data:", response.content)
