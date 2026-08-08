from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('secure_auth.urls')),
    path('visitor-analytics/', include('visitor_analytics.urls')),
]