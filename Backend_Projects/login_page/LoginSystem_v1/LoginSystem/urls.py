from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('secure_auth.urls')),  # <── Add quotes around 'secure_auth.urls'!
]