from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q
from rest_framework.views import APIView
from ..forms import RegisterForm
from django.db import transaction
from rest_framework.permissions import AllowAny
from ..utils import generate_otp, send_otp_email
from django.middleware.csrf import get_token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from ..serializers import RegisterSerializer, LoginSerializer
User = get_user_model()

def auth_page(request):
    get_token(request)
    return render(request, "auth/auth.html")
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    # throttle_classes = [AnonRateThrottle]
    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data
        )


        if not serializer.is_valid():
            return Response(
                {"success":False,
                 "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        return Response(
            {"success": True, "message":"Account created successfully"},
            status=status.HTTP_201_CREATED
        )
    
class LoginAPIView(APIView):
    permission_classes=[AllowAny]
    # throttle_classes = [AnonRateThrottle]
    def post(self,request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"success":False,
                 "message": serializer.errors.get(
                    "non_field_errors",
                    ["Validation errors"]
                )[0],
                "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.validated_data['user']
        auth_login(request, user)
        return Response(
            {
            'success': True,
            "user":{"id":user.id,"email":user.email}
            },
            status=status.HTTP_200_OK
        )
class LogoutAPIView(APIView):
    premission_classes = [IsAuthenticated]

    def post(self,request):
        auth_logout(request)
        return Response(
            {
                "success":True,
                "message":"Logged out successfully"
            },
            status=status.HTTP_200_OK
        )
        
        

# def register_view(request):

#     if request.method == "POST":

#         form = RegisterForm(request.POST)

#         if not form.is_valid():
#             return render(request, "auth/auth.html", {"register_form": form})
#         try:
#             with transaction.atomic():

#                 user = form.save()

#                 otp = generate_otp(user, "verify")
#                 send_otp_email(otp)

#                 request.session["email_verify_user_id"] = user.id

#             return redirect("verify-email-otp")

#         except Exception:
#             messages.error(request, "Registration failed", extra_tags="register")
#             return render(request, "auth/auth.html", {"register_form": form})

#     return redirect("/auth/?mode=signup")


# def login_view(request):
#     if request.method != "POST":
#         return redirect("auth")

#     login_input = request.POST.get("login")
#     password = request.POST.get("password")

#     try:
#         user_obj = User.objects.get(
#             Q(username=login_input) |
#             Q(email=login_input)
#         )

#         user = authenticate(request, username=user_obj.username, password=password)

#         if user and user.is_active:
#             login(request, user)
#             messages.success(request, "Logged in successfully.", extra_tags="login")
#             return redirect("home")

#         messages.error(request, "Invalid credentials", extra_tags="login")

#     except User.DoesNotExist:
#         messages.error(request, "User not found", extra_tags="login")

#     return redirect("auth")


# def logoutUser(request):
#     if request.method == "POST":
#         logout(request)
#         return redirect("home")
