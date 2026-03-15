from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    # Frontend pages
    register_page,
    login_page,
    profile_page,

    # API views
    StudentRegisterView,
    StudentLoginView,
    OTPRequestView,
    OTPVerifyView,
    StudentLogoutView,
    StudentProfileView,
)

urlpatterns = [

    # ── Frontend Pages ──────────────────────────
    path('',          login_page,    name='login'),
    path('register/', register_page, name='register'),
    path('profile/',  profile_page,  name='profile'),

    # ── API Endpoints ───────────────────────────
    path('api/auth/register/',      StudentRegisterView.as_view(), name='api_register'),
    path('api/auth/login/',         StudentLoginView.as_view(),    name='api_login'),
    path('api/auth/otp/request/',   OTPRequestView.as_view(),      name='api_otp_request'),
    path('api/auth/otp/verify/',    OTPVerifyView.as_view(),       name='api_otp_verify'),
    path('api/auth/logout/',        StudentLogoutView.as_view(),   name='api_logout'),
    path('api/auth/profile/',       StudentProfileView.as_view(),  name='api_profile'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(),    name='api_token_refresh'),

]
