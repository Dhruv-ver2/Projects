# core/views.py
from django.shortcuts import render

def home_view(request):
    """
    Renders the main homepage for this project.
    """
    return render(request, 'index.html')