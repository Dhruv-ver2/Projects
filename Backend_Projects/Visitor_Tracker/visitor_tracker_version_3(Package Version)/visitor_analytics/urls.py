# visitor_analytics/urls.py
from django.urls import path
from .views import update_browser_info

urlpatterns = [
    # Listens for POST requests at /analytics/verify-browser/
    path('verify-browser/', update_browser_info, name='verify_browser'),
]