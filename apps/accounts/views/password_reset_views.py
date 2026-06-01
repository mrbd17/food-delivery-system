from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
import time
from ..utils import generate_otp, send_otp_email, verify_otp

User = get_user_model()

def request_password_reset(request):
    if request.method == "POST":

        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email not found")
            return redirect("password-reset-request")

        otp = generate_otp(user, "reset")
        send_otp_email(otp)

        request.session["password_reset_user_id"] = user.id
        return redirect("password-reset-verify")

    return render(request, "auth/forgot-password.html")
    

def verify_password_reset_otp(request):

    if "password_reset_user_id" not in request.session:
        return redirect("password-reset-request")

    if request.method == "POST":

        code = request.POST.get("otp_code")
        user = User.objects.get(id=request.session["password_reset_user_id"])

        success, msg = verify_otp(user, code, "reset")

        if success:
            request.session["password_reset_verified"] = True
            return redirect("password-reset-confirm")

        messages.error(request, msg)

    return render(request, "auth/verify_reset_otp.html")
    

def reset_password(request):
    if not request.session.get("password_reset_verified"):
        return redirect("password-reset-request")

    if request.method == "POST":

        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("password-reset-confirm")

        user = User.objects.get(id=request.session["password_reset_user_id"])
        user.set_password(password)
        user.save()

        del request.session["password_reset_user_id"]
        del request.session["password_reset_verified"]

        messages.success(request, "Password updated successfully")
        return redirect("auth")

    return render(request, "auth/reset_password.html")

def resend_password_reset_otp(request):
    if "password_reset_user_id" not in request.session:
        return redirect("password-reset-request")

    now = time.time()
    last = request.session.get("password_reset_last_resend")

    if last and now - last < 60:
        messages.warning(
            request,
            "Please wait before requesting again."
        )
        return redirect("password-reset-verify")

    user_id = request.session["password_reset_user_id"]
    user = User.objects.get(id=user_id)

    otp = generate_otp(user, "reset")
    send_otp_email(otp)

    request.session["password_reset_last_resend"] = now

    messages.success(
        request,
        "A new reset code has been sent to your email."
    )
    return redirect("password-reset-verify")
