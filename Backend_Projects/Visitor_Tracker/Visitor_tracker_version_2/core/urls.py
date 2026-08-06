from django.contrib import admin
from django.urls import path
from analytics.views import home_view, update_browser_info

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('api/verify-browser/', update_browser_info, name='verify_browser'),
]