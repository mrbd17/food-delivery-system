from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status


class RegisterAPITest(TestCase):
    def test_user_can_register(self):
        data = {
            "username": "mahmoud",
            "email": "mahmod@gmail.com",
            "password1": "strongPassword123",
            "password2": "strongPassword123",
            "first_name": "mahmoud",
            "last_name": "rabai",
        }
        response = self.client.post("/api/account/register/", data)
        print(response.json)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="mahmod@gmail.com").exists())
        user = User.objects.get(email="mahmod@gmail.com")
        self.assertTrue(user.first_name == "mahmoud")
        self.assertTrue(user.check_password("strongPassword123"))


class LoginAPITest(TestCase):
    def setUp(self):
        self.data = {
            "username": "mahmoud",
            "email": "mahmod@gmail.com",
            "password1": "strongPassword123",
            "password2": "strongPassword123",
            "first_name": "mahmoud",
            "last_name": "rabai",
        }
        self.client.post("/api/account/register/", self.data)
        self.correct_data = {
            "email": "mahmod@gmail.com",
            "password": "strongPassword123",
        }
        self.wrong_data = {
            "email": "mahmod@gmail.com",
            "password": "wrongPassword123",
        }
        self.url = "/api/account/login/"

        self.response = self.client.post

    def test_user_can_login(self):
        response = self.response(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], True)

        self.assertEqual(response.data["user"], {"id": 1, "email": "mahmod@gmail.com"})

    def test_user_cannot_login_with_wrong_password(self):
        response = self.response(self.url, self.wrong_data)

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("non_field_errors", response.data["errors"])

        self.assertEqual(
            response.data["errors"]["non_field_errors"][0], "Invalid credentials"
        )
