import logging
import time

from django.contrib.auth import get_user_model
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..utils import generate_otp, send_otp_email, verify_otp as verifyOTP

logger = logging.getLogger(__name__)
User = get_user_model()


def verify_otp(request):
    return render(request, "auth/verify_otp.html")

class SendOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"success": False, "message": "Email required"})

        try:
            user = User.objects.get(email=email, is_active=False)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "User not Found or already verified"},
                status=status.HTTP_404_NOT_FOUND,
            )
        email_otp = generate_otp(user, "verify")
        send_otp_email(email_otp)

        token = self.create_verification_token(user)
        logger.info(f"Verifiction Token {token}")

        return Response(
            {
                "success": True,
                "message": "OTP sent successfully",
                "verification_token": token,
            }
        )

    @staticmethod
    def create_verification_token(user):
        signer = TimestampSigner()
        return signer.sign(str(user.id))


class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        otp_code = request.data.get("otp_code")
        verification_token = request.data.get("verification_token")

        if not otp_code or not verification_token:
            return Response(
                {"success": False, "message": "OTP and Token required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = self.verify_token(verification_token)
            user = User.objects.get(id=user_id)
        except (ValueError, User.DoesNotExist):
            return Response(
                {"success": False, "message": "Invalid or Token Expired"},
                status=status.HTTP_404_NOT_FOUND,
            )

        success, msg = verifyOTP(user, otp_code, "verify")

        if success:
            user.is_active = True
            user.save(update_fields=["is_active"])
            logger.info(user)
            return Response(
                {"success": True, "message": "Verified Successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": False, "message": msg},
            status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def verify_token(token):
        signer = TimestampSigner()
        try:
            return signer.unsign(token, max_age=3600)
        except SignatureExpired:
            raise ValueError("Token Expired")

        except BadSignature:
            raise ValueError("Invalid Token")



class ResendOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        verification_token = request.data.get("verification_token")

        if not verification_token:
            return Response(
                {"success": False, "message": "Token required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = self.get_user_id_from_token(verification_token)
            user = User.objects.get(id=user_id)
        except (ValueError, User.DoesNotExist):
            return Response(
                {"success": False, "message": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        last_resend = request.session.get(f"otp_resend_{user.id}")
        now = time.time()

        if last_resend and now - last_resend < 60:
            return Response(
                {
                    "success": False,
                    "message": "Please wait before requesting again",
                    "retry_after": int(60 - (now - last_resend)),
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        otp = generate_otp(user, "verify")
        send_otp_email(otp)

        request.session[f"otp_resend_{user.id}"] = now

        return Response(
            {"success": True, "message": "OTP resent"}, status=status.HTTP_200_OK
        )

    @staticmethod
    def get_user_id_from_token(token):
        from django.core.signing import TimestampSigner

        signer = TimestampSigner()
        try:
            return signer.unsign(token, max_age=3600)
        except SignatureExpired:
            raise ValueError("Token Expired")

        except BadSignature:
            raise ValueError("Invalid Token")
