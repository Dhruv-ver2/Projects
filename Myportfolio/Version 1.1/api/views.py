from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import json
import os
from datetime import datetime

@csrf_exempt
def contact_form_submit(request):
    if request.method == 'POST':
        print("\n--- NEW REQUEST RECEIVED ---")
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            subject = data.get('subject')
            message = data.get('message')
            print("Step 1: Form data successfully parsed.")

            # --- 1. Attempt to Send the Email ---
            try:
                email_subject = f"New Contact Form Submission: {subject}"
                email_message = f"""
                You have received a new message from your portfolio contact form.

                Name: {name}
                Email: {email}
                
                Message:
                {message}
                """
                
                print("Step 2: Attempting to send email...")
                send_mail(
                    email_subject,
                    email_message,
                    settings.EMAIL_HOST_USER,  # From email
                    [settings.EMAIL_HOST_USER],  # To email (sending to yourself)
                    fail_silently=False,
                )
                print("Step 3: Email sent successfully!")

            except Exception as e:
                print(f"!!! EMAIL FAILED: {e}") # This will show us the email error

            # --- 2. Attempt to Save to a Text File ---
            try:
                print("Step 4: Attempting to write to file...")
                file_path = os.path.join(settings.BASE_DIR, 'contact_submissions.txt')
                with open(file_path, 'a') as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"--- Submission at {timestamp} ---\n")
                    f.write(f"Name: {name}\n")
                    f.write(f"Email: {email}\n")
                    f.write(f"Subject: {subject}\n")
                    f.write(f"Message: {message}\n")
                    f.write("-----------------------------------------\n\n")
                print("Step 5: File written successfully!")

            except Exception as e:
                print(f"!!! FILE WRITE FAILED: {e}") # This will show us the file error

            return JsonResponse({'status': 'success', 'message': 'Form submitted successfully!'})

        except Exception as e:
            print(f"!!! CRITICAL ERROR: An unexpected error occurred: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
