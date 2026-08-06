from django.shortcuts import render
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_step1_view, name='signup_step1'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('activate-account/', views.activate_password_view, name='activate_password'),
]