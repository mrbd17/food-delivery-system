from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from ..utils import generate_otp, send_otp_email, verify_otp


class TestOTPUtilies(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mahmoud", email="mahmoud@gmail.com", password="12345"
        )

    @patch("accounts.utils.random.randint")
    def test_generate_otp(self, mock_randint):

        mock_randint.return_value = "123456"

        email_otp = generate_otp(user=self.user, purpose="verify")
        self.assertEqual(email_otp.user, self.user)
        self.assertEqual(email_otp.otp, "123456")
        self.assertEqual(email_otp.purpose, "verify")
        self.assertFalse(email_otp.is_verified)

    @patch("accounts.utils.send_mail")
    def test_send_otp_email(self, mock_send_mail):

        email_otp = generate_otp(user=self.user, purpose="verify")

        send_otp_email(email_otp)

        mock_send_mail.assert_called_once_with(
            subject="Your OTP Code",
            message=f"Your OTP is {email_otp.otp}. it expires in 5 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_otp.user.email],
            fail_silently=False,
        )

    def test_verify_otp_success(self):

        email_otp = generate_otp(user=self.user, purpose="verify")

        success, message = verify_otp(
            user=self.user, input_otp=email_otp.otp, purpose="verify"
        )

        self.assertTrue(success)

        self.assertEqual(message, "OTP verified successfully.")

    def test_verify_otp_failed(self):

        email_otp = generate_otp(user=self.user, purpose="verify")
        success, message = verify_otp(
            user=self.user, input_otp="123456", purpose="verify"
        )
        email_otp.refresh_from_db()

        self.assertFalse(success)

        self.assertEqual(message, "Incorrect OTP.")

        self.assertEqual(email_otp.attempts, 1)
