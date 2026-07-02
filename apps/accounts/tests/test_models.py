from django.test import TestCase
from apps.accounts.models import Profile, EmailOTP
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


class TestProfileModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="mahmoud", password="12345")

        self.profile = self.user.profile

    def test_profile_created_automatically(self):

        self.assertIsInstance(self.profile, Profile)

    def test_default_role(self):

        self.assertEqual(self.profile.role, "customer")

    def test_default_theme(self):
        self.assertEqual(self.profile.theme, "light")

    def test_profile_str(self):

        self.assertEqual(str(self.profile), "mahmoud")


class TestEmialOtp(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="mahmoud", password="12345")

    def test_otp_is_expired(self):

        otp = EmailOTP.objects.create(
            user=self.user,
            otp="123456",
            expires_at=timezone.now() - timedelta(minutes=5),
            purpose="verify",
        )

        self.assertTrue(otp.is_expired())

    def test_otp_not_expired(self):

        otp = EmailOTP.objects.create(
            user=self.user,
            otp="123456",
            expires_at=timezone.now() + timedelta(minutes=5),
            purpose="verify",
        )

        self.assertFalse(otp.is_expired())
