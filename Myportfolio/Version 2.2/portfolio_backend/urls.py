"""
URL configuration for portfolio_backend project.
The `urlpatterns` list routes URLs to views. For more information please see:
 https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
 1. Add an import: from . import views
 2. Add a URL to urlpatterns: path('', views.home, name='home')
Class-based views
 1. Add an import: from other_app import views
 2. Add a URL to urlpatterns: path('', views.Home.as_view(), name='home')
Including another URLconf
 1. Import the include() function: from django.urls import include, path
 2. Add a URL to urlpatterns: path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Include API urls (home, contact, send-discord)
    path('', include('api.urls')),
]

# ✅ FIXED: Serve static files from STATIC_ROOT during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
