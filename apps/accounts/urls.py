from django.urls import path

from .views import auth_views as auth, email_verification_views as email, password_reset_views as password

from .views import (
    profile_views as profile,
)

urlpatterns = [
    # =========================
    # AUTH
    # =========================
    path("auth/", auth.auth_page, name="auth"),
    path("google/", auth.GoogleAuth.as_view(), name='google_auth'),
    path("register/", auth.RegisterAPIView.as_view(), name="register"),
    path("login/", auth.LoginAPIView.as_view(), name="login"),
    path("logout/", auth.LogoutAPIView.as_view(), name="logout"),

    # =========================
    # EMAIL VERIFICATION
    # =========================
    path("email/verify-otp/",email.verify_otp, name="verify-otp"),
    path('email/otp/send/', email.SendOTPAPIView.as_view(), name='api-send-otp'),
    path('email/otp/verify/', email.VerifyOTPAPIView.as_view(), name='api-verify-otp'),
    path('email/otp/resend/', email.ResendOTPAPIView.as_view(), name='api-resend-otp'),
    # =========================
    # PASSWORD RESET
    # =========================
    path("password/reset/", password.request_password_reset, name="password-reset-request"),
    path("password/reset/verify/", password.verify_password_reset_otp, name="password-reset-verify"),
    path("password/reset/resend/", password.resend_password_reset_otp, name="password-reset-resend"),
    path("password/reset/new/", password.reset_password, name="password-reset-confirm"),

    # =========================
    # ACCOUNT
    # =========================
    path("account/", profile.account_shell, name="account_shell"),

    # =========================
    # API
    # =========================
    path("overview/", profile.AccountOverviewAPI.as_view(), name="overview"),
    path("personal/", profile.PersonalInfoView.as_view(), name="personal"),
    path("personal/change-name/", profile.ChangeNameView.as_view()),
    path("personal/change-phone/", profile.ChangePhoneView.as_view()),
    path("personal/change-email/", profile.ChangeEmailView.as_view()),
    path("personal/change-avatar/", profile.AvatarUploadView.as_view()),
    path("personal/change-password/", profile.ChangePasswordView.as_view()),
]
