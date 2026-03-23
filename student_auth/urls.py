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
    # New GET API's <-- add these 2
    StudentDetailView,
    StudentListView,
    #UPdate and put
    StudentUpdateView,
    StudentDeleteView,
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

    # GET APIs
    path('api/students/',      StudentListView.as_view(),   name='api_student_list'),
    path('api/students/<int:pk>/', StudentDetailView.as_view(), name='api_student_detail'),
    path('api/students/<int:pk>/update/', StudentUpdateView.as_view(), name='api_student_update'),
    path('api/students/<int:pk>/delete/', StudentDeleteView.as_view(), name='api_student_delete'),
]
