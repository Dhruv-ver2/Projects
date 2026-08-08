# core/urls.py
from django.contrib import admin
from django.urls import path, include
from .views import home_view  # Import home_view from core views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Main website homepage
    path('', home_view, name='home'),
    
    # 2. Reusable tracking package routes (/visitor_analytics/verify-browser/)
    path('visitor-analytics/', include('visitor_analytics.urls')),
]