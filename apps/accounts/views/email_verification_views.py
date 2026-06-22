from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import render
from django.core.signing import TimestampSigner, SignatureExpired
from django.utils import timezone
import time

from ..serializers import RegisterSerializer, LoginSerializer
from ..models import EmailOTP as OTP
from ..utils import generate_otp, send_otp_email, verify_otp as verifyOTP
import logging
logger = logging.getLogger(__name__)
User = get_user_model()

def verify_otp(request):
    return render(request, "auth/verify_otp.html")
class SendOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {"success":False, "message":"Email required"}
            )

        try:
            user = User.objects.get(email=email, is_active=False)
        except User.DoesNotExist:
            return Response(
                {"success":False, "message": "User not Found or already verified"}
                , status=status.HTTP_404_NOT_FOUND
            )
        email_otp = generate_otp(user, "verify")
        send_otp_email(email_otp)

        token = self.create_verification_token(user)
        logger.info(f"Verifiction Token {token}")

        return Response(
            {
                "success":True,
                "message": "OTP sent successfully",
                "verification_token": token
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
                {"success":False, "message":"OTP and Token required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_id = self.verify_token(verification_token)
            user = User.objects.get(id=user_id)
        except (ValueError, User.DoesNotExist):
            return Response(
                {"success":False, "message":"Invalid or Token Expired"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        success, msg = verifyOTP(user , otp_code , 'verify')

        if success:
            user.is_active = True
            user.save(update_fields=['is_active'])
            logger.info(user)
            return Response(
                {"success":True, "message":"Verified Successfully"},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"success":False, "message":msg}
        )
    @staticmethod
    def verify_token(token):
        signer = TimestampSigner()

        try: 
            return signer.unsign(token, max_age=3600)
        except SignatureExpired:
            raise ValueError("Token Expired")
    
class ResendOTPAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        verification_token = request.data.get('verification_token')
        
        if not verification_token:
            return Response(
                {"success": False, "message": "Token required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_id = self.get_user_id_from_token(verification_token)
            user = User.objects.get(id=user_id)
        except (ValueError, User.DoesNotExist):
            return Response(
                {"success": False, "message": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
        last_resend = request.session.get(f"otp_resend_{user.id}")
        now = time.time()
        
        if last_resend and now - last_resend < 60:
            return Response(
                {
                    "success": False,
                    "message": "Please wait before requesting again",
                    "retry_after": int(60 - (now - last_resend))
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        otp = generate_otp(user, "verify")
        send_otp_email(otp)
        
        request.session[f"otp_resend_{user.id}"] = now
        
        return Response(
            {"success": True, "message": "OTP resent"},
            status=status.HTTP_200_OK
        )
    
    @staticmethod
    def get_user_id_from_token(token):
        from django.core.signing import TimestampSigner
        signer = TimestampSigner()
        return signer.unsign(token, max_age=3600)





































# import time

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth import get_user_model

# from ..utils import generate_otp, send_otp_email, verify_otp

# User = get_user_model()

# def send_email_verification_otp(request):
#     email_otp = generate_otp(request.user)
#     send_otp_email(email_otp)
#     return redirect("verify-email-otp")

# def resend_email_otp(request):

#     if "email_verify_user_id" not in request.session:
#         return redirect("auth")

#     now = time.time()
#     last = request.session.get("email_verify_last_resend")

#     if last and now - last < 60:
#         messages.warning(request, "Please wait before requesting again.")
#         return redirect("verify-email-otp")

#     user = User.objects.get(id=request.session["email_verify_user_id"])

#     otp = generate_otp(user, "verify")
#     send_otp_email(otp)

#     request.session["email_verify_last_resend"] = now

#     messages.success(request, "A new OTP has been sent.")
#     return redirect("verify-email-otp")


# def verify_email_otp(request):

#     if "email_verify_user_id" not in request.session:
#         return redirect("auth")

#     if request.method == "POST":

#         code = request.POST.get("otp_code")
#         user = User.objects.get(id=request.session["email_verify_user_id"])

#         success, msg = verify_otp(user, code, "verify")

#         if success:
#             user.is_active = True
#             user.save()

#             del request.session["email_verify_user_id"]
#             request.session.pop("email_verify_last_resend", None)

#             messages.success(request, "Email verified successfully.")
#             return redirect("/auth/?mode=login")

#         messages.error(request, msg)

#     return render(request, "auth/verify_email.html")
    
