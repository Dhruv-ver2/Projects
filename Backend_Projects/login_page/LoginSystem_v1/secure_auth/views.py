import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
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
        
        # 3. Create the record in our single table (Flags default to False automatically)
        user_record = UserAccount.objects.create(
            first_name=fname,
            last_name=lname,
            email=user_email,
            otp_code=generated_otp
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
    # Retrieve the email stored in the session memory from Step 1
    user_email = request.session.get("verifying_email")
    
    if not user_email:
        return redirect("signup_step1")
        
    error_message = None
    
    if request.method == "POST":
        user_input_otp = request.POST.get("otp")
        
        # Look up the row in our single unified table
        try:
            account = UserAccount.objects.get(email=user_email)
            
            # Check if the code matches perfectly
            if account.otp_code == user_input_otp:
                # ──> Success! Turn the verified_email flag to True
                account.email_verified = True
                account.save()
                
                # Send them directly to Step 3 (Password setting)
                return redirect("activate_password")
            else:
                # ──> Failure! Assign the custom text line message
                error_message = "The OTP didn't match."
                
        except UserAccount.DoesNotExist:
            return redirect("signup_step1")
            
    return render(request, "secure_auth/verify_otp.html", {"error_message": error_message})


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