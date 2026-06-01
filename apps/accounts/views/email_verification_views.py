import time

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

from ..utils import generate_otp, send_otp_email, verify_otp

User = get_user_model()

def send_email_verification_otp(request):
    email_otp = generate_otp(request.user)
    send_otp_email(email_otp)
    return redirect("verify-email-otp")

def resend_email_otp(request):

    if "email_verify_user_id" not in request.session:
        return redirect("auth")

    now = time.time()
    last = request.session.get("email_verify_last_resend")

    if last and now - last < 60:
        messages.warning(request, "Please wait before requesting again.")
        return redirect("verify-email-otp")

    user = User.objects.get(id=request.session["email_verify_user_id"])

    otp = generate_otp(user, "verify")
    send_otp_email(otp)

    request.session["email_verify_last_resend"] = now

    messages.success(request, "A new OTP has been sent.")
    return redirect("verify-email-otp")


def verify_email_otp(request):

    if "email_verify_user_id" not in request.session:
        return redirect("auth")

    if request.method == "POST":

        code = request.POST.get("otp_code")
        user = User.objects.get(id=request.session["email_verify_user_id"])

        success, msg = verify_otp(user, code, "verify")

        if success:
            user.is_active = True
            user.save()

            del request.session["email_verify_user_id"]
            request.session.pop("email_verify_last_resend", None)

            messages.success(request, "Email verified successfully.")
            return redirect("/auth/?mode=login")

        messages.error(request, msg)

    return render(request, "auth/verify_email.html")
    
