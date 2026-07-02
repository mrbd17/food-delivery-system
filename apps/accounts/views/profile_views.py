from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from ..models import Profile
from ..serializers import (
    AccountOverviewSerializer,
    PersonalInfoSerializer,
    ChangeNameSerializer,
    ChangePhoneSerializer,
    ChangeEmailSerializer,
    ChangePasswordSerializer,
    AvatarUploadSerializer,
)

from django.contrib.auth import update_session_auth_hash

User = get_user_model()


@login_required
def account_shell(request):
    return render(request, "shell.html")


class AccountOverviewAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = AccountOverviewSerializer({"user": request.user})
        return Response(serializer.data)


class PersonalInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = PersonalInfoSerializer(request.user)
        return Response({"success": True, "data": serializer.data})


class ChangeNameView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):

        serializer = ChangeNameSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data})

        return Response(serializer.errors, status=400)


class ChangePhoneView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):

        serializer = ChangePhoneSerializer(instance=request.user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            serializer.update(request.user, serializer.validated_data)

            return Response({"success": True, "phone": request.user.profile.phone})

        return Response(serializer.errors, status=400)


class ChangeEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):

        serializer = ChangeEmailSerializer(request.user, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({"success": True, "email": serializer.data["email"]})

        return Response(serializer.errors, status=400)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            user = serializer.save()
            update_session_auth_hash(request, user)

            return Response({"success": True})

        return Response(serializer.errors, status=400)


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile, _ = Profile.objects.get_or_create(user=request.user)

        serializer = AvatarUploadSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Avatar updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
