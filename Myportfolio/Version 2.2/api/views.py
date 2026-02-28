import requests
import json
import os
from django.shortcuts import render
from django.http import JsonResponse

def home_view(request):
    """Renders the main portfolio page."""
    return render(request, 'index.html')

def contact_view(request):
    """Renders the extraordinary contact page."""
    return render(request, 'contact.html')

def contact_to_discord(request):
    """Handles form submission and sends it to Discord Webhook."""
    if request.method == "POST":
        try:
            # Get data from the frontend form
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject', 'New Portfolio Inquiry')
            message = request.POST.get('message')

            # Fetch Webhook URL from .env
            webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

            if not webhook_url:
                return JsonResponse({"status": "error", "message": "Server configuration error."}, status=500)

            # Create the Discord Embed (Color 0x00e5ff matches your Cyan glow)
            payload = {
                "username": "Portfolio Bot",
                "embeds": [{
                    "title": f"📩 {subject}",
                    "color": 0x00e5ff,
                    "fields": [
                        {"name": "Sender", "value": name, "inline": True},
                        {"name": "Email", "value": email, "inline": True},
                        {"name": "Message", "value": message, "inline": False}
                    ],
                    "footer": {"text": "Dhruv-ver2 Portfolio v1.4"}
                }]
            }

            response = requests.post(
                webhook_url, 
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 204:
                return JsonResponse({"status": "success"})
            return JsonResponse({"status": "error"}, status=400)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)