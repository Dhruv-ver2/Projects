from django.urls import path
from .views import dashboard_view, delete_word_view, update_word_view

# These routes only activate AFTER being passed through the front door include statement!
urlpatterns = [
    path('', dashboard_view),  # Matches the homepage dashboard
    path('delete-word/<int:word_id>/', delete_word_view),
    path('update-word/<int:word_id>/', update_word_view),
]