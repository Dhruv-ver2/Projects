from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone  # 🌟 Added for industry-standard timestamping
import random
from datetime import timedelta
from .models import UserAccount

def signup_step1_view(request):
    if request.method == "POST":
        # 1. Grab the inputs from the frontend HTML form
        fname = request.POST.get("first_name")
        lname = request.POST.get("last_name")
        user_email = request.POST.get("email")
        
        # 🛡️ 1.5. Security Perimeter: Reject if email already belongs to an active user
        if UserAccount.objects.filter(email=user_email, active_status=True).exists():
            return render(request, "secure_auth/signup_step1.html", {
                "error_message": "This email address is already registered inside our system.",
                "typed_fname": fname,
                "typed_lname": lname
            })
            
        # 🧹 Cleanup: Delete unactivated/stale sessions trying to use the same email
        UserAccount.objects.filter(email=user_email, active_status=False).delete()
        
        # 2. Generate a random 6-digit string code
        generated_otp = str(random.randint(100000, 999999))
        print(f"OTP: {generated_otp}")
        
        # 3. Create the record in our single table (Flags default to False automatically)
        user_record = UserAccount.objects.create(
            first_name=fname,
            last_name=lname,
            email=user_email,
            otp_code=generated_otp,
            # 🌟 THE LOGIC PATCH: Log the precise creation time for expiration calculation
            otp_created_at=timezone.now()
        )
        
        # 4. Fire the true network email packet to the user
        send_mail(
            subject="🔑 Your Verification OTP",
            message=f"Hello {fname},\n\nYour 6-digit verification code is: {generated_otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        
        # 5. Lock their email into a session memory string so we know who is verifying on page 2
        request.session["verifying_email"] = user_email
        
        # 6. Redirect them instantly to the OTP verification view page
        return redirect("verify_otp")
        
    return render(request, "secure_auth/signup_step1.html")


# Add this function to the bottom of your secure_auth/views.py file:

def verify_otp_view(request):
    session_email = request.session.get("verifying_email")
    
    try:
        user_record = UserAccount.objects.get(email=session_email)
    except UserAccount.DoesNotExist:
        return redirect("signup_step1")

    if request.method == "POST":
        user_submitted_otp = request.POST.get("otp")
        
        # 🛡️ Time Gatekeeper: Check if the OTP has aged past 5 minutes
        if user_record.otp_created_at:
            expiry_time = user_record.otp_created_at + timedelta(minutes=5)
            if timezone.now() > expiry_time:
                return render(request, "secure_auth/verify_otp.html", {
                    "error_message": "Your verification code has expired. Please sign up again to receive a new one."
                })
        
        # Validation Gatekeeper: Check if code matches
        if user_record.otp_code == user_submitted_otp and user_record.otp_code is not None:
            user_record.otp_code = None
            user_record.email_verified = True
            user_record.save()
            return redirect("activate_password")
        else:
            return render(request, "secure_auth/verify_otp.html", {
                "error_message": "Invalid verification code. Please try again."
            })
            
    # 🌟 GET REQUEST LOGIC: Calculate exactly how many seconds are left for the live UI timer
    time_left_seconds = 0
    if user_record.otp_created_at:
        expiry_time = user_record.otp_created_at + timedelta(minutes=5)
        remaining_time = expiry_time - timezone.now()
        # Convert total time difference into absolute raw seconds (capped at 0)
        time_left_seconds = max(0, int(remaining_time.total_seconds()))

    return render(request, "secure_auth/verify_otp.html", {
        "time_left": time_left_seconds
    })

def resend_otp_view(request):
    # 1. Look up who is currently trying to verify using session memory
    session_email = request.session.get("verifying_email")
    
    if not session_email:
        return redirect("signup_step1")
        
    try:
        user_record = UserAccount.objects.get(email=session_email)
        
        # 2. Generate a fresh 6-digit string code
        new_otp = str(random.randint(100000, 999999))
        print(f"NEW RESENT OTP: {new_otp}")  # Debug print
        
        # 3. Update the database row with the new code and a fresh birth timestamp
        user_record.otp_code = new_otp
        user_record.otp_created_at = timezone.now()
        user_record.save()
        
        # 4. Mail out the new token packet
        send_mail(
            subject="🔑 Your New Verification OTP",
            message=f"Hello {user_record.first_name},\n\nYour new 6-digit verification code is: {new_otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[session_email],
            fail_silently=False,
        )
        
    except UserAccount.DoesNotExist:
        return redirect("signup_step1")
        
    # 5. Bounce them back to the same verification page where a brand new 5:00 countdown begins!
    return redirect("verify_otp")

def activate_password_view(request):
    # 1. Peek into session memory to identify which user is setting their password
    user_email = request.session.get("verifying_email")
    
    if not user_email:
        return redirect("signup_step1")
        
    if request.method == "POST":
        raw_password = request.POST.get("password")
        
        try:
            # 2. Fetch their record row from our single table
            account = UserAccount.objects.get(email=user_email)
            
            # 3. For now, we will store the string (we will add hashing next!)
            account.password_hash = raw_password 
            
            # 4. Success! Turn the active_status flag to True
            account.active_status = True
            account.save()
            
            # 5. Clear out the temporary tracking session memory
            del request.session["verifying_email"]
            
            return render(request, "secure_auth/success.html", {"first_name": account.first_name})
            
        except UserAccount.DoesNotExist:
            return redirect("signup_step1")
            
    return render(request, "secure_auth/activate_password.html")