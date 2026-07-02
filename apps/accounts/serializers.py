from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Profile
from django.contrib.auth import authenticate
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, allow_blank=False)
    mode = serializers.ChoiceField(choices=["login", "signup"], required=True)

    def validate_token(self, value):
        if not value or len(value) < 10:
            raise serializers.ValidationError("Invalid token Format")
        return value

    def validate_mode(self, value):
        if value not in ["login", "signup"]:
            raise serializers.ValidationError("Mode must be 'Login' or 'Signup'")
        return value


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "passwords dose'nt match"})
        validate_password(attrs["password1"])

        return attrs

    def create(self, validate_data):
        user = User.objects.create_user(
            username=validate_data["email"],
            email=validate_data["email"],
            first_name=validate_data["first_name"],
            last_name=validate_data["last_name"],
            password=validate_data["password1"],
        )
        user.is_active = False
        user.save(update_fields=["is_active"])
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("Account is not activated")
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        attrs["user"] = user
        return attrs


class UserMiniSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="profile.role")
    avatar = serializers.ImageField(source="profile.avatar")
    theme = serializers.CharField(source="profile.theme")
    phone = serializers.CharField(source="profile.phone")
    is_verified = serializers.BooleanField(source="profile.is_verified")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "last_login",
            "role",
            "avatar",
            "theme",
            "phone",
            "is_verified",
        ]


class AccountOverviewSerializer(serializers.Serializer):
    user = UserMiniSerializer()


class PersonalInfoSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="profile.role")
    avatar = serializers.ImageField(source="profile.avatar")
    theme = serializers.CharField(source="profile.theme")
    phone = serializers.CharField(source="profile.phone")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "last_login",
            "role",
            "avatar",
            "theme",
            "phone",
        ]


class ChangeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
        ]


class ChangePhoneSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def update(self, instance, validated_data):

        profile = instance.profile
        profile.phone = validated_data["phone"]
        profile.save()
        return instance

    def save(self, **kwargs):
        return self.update(self.instance, self.validated_data)


class ChangeEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email"]


class AvatarUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["avatar"]


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate_current_password(self, value):

        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")

        return value

    def save(self):

        user = self.context["request"].user
        new_password = self.validated_data["new_password"]

        user.set_password(new_password)
        user.save()

        return user
