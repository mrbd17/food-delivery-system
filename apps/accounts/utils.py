import random
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import EmailOTP


def generate_otp(user, purpose, minutes_valid=5):
    otp = f"{random.randint(100000, 999999)}"
    expires_at = timezone.now() + timedelta(minutes=minutes_valid)

    email_otp = EmailOTP.objects.create(
        user=user, otp=otp, expires_at=expires_at, purpose=purpose
    )
    return email_otp


def send_otp_email(email_otp):
    send_mail(
        subject="Your OTP Code",
        message=f"Your OTP is {email_otp.otp}. it expires in 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email_otp.user.email],
        fail_silently=False,
    )


def verify_otp(user, input_otp, purpose):
    try:
        email_otp = EmailOTP.objects.filter(
            user=user,
            purpose=purpose,
            is_verified=False,
        ).latest("created_at")

    except EmailOTP.DoesNotExist:
        return False, "No OTP found."

    if email_otp.is_expired():
        return False, "OTP expired."

    if email_otp.attempts >= 3:
        return False, "Maximum attempts exceeded."

    if email_otp.otp == input_otp:
        email_otp.delete()
        return True, "OTP verified successfully."

    else:
        email_otp.attempts += 1
        email_otp.save()
        return False, "Incorrect OTP."
