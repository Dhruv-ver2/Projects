from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

# A basic single-page view for local testing
def home_view(request):
    return HttpResponse("""
        <div style='font-family: sans-serif; text-align: center; padding-top: 50px;'>
            <h1>🚀 Visitor Tracker Test Page</h1>
            <p>Your visit is being recorded by the custom middleware!</p>
            <p><a href='/admin/'>Go to Django Admin Panel</a></p>
        </div>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
]