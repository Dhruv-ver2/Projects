from django.contrib import admin
from django.urls import path, include  # <-- 1. CRITICAL: Import the 'include' function!

urlpatterns = [
    path('admin/', admin.site.urls),  # Sends admin traffic to the built-in system
    
    # 2. THE MASTER CONNECTION:
    # This tells Django: "Take any request hitting the root domain ('') 
    # and pass it directly into the vault app's custom urls.py file!"
    path('', include('vault.urls')), 
]