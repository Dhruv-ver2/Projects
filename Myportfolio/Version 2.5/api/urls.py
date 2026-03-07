from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('contact/', views.contact_view, name='contact'),
    path('send-discord/', views.contact_to_discord, name='send_discord'),
    path('scripts-hub/', views.scripts_hub_view, name='scripts_hub'), # New Route
]