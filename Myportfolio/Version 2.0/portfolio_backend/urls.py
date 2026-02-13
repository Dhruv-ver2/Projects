from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # This gives you access to the Django Admin panel
    path('admin/', admin.site.urls),
    
    # This tells Django to use the URL patterns defined in your 'api' app
    # This connects your index.html, contact.html, and Discord logic
    path('', include('api.urls')),
]