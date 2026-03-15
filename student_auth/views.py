from django.shortcuts import render
from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import Student, OTPRecord
from .serializers import (
    StudentRegistrationSerializer,
    StudentLoginSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    StudentProfileSerializer,
)
from .utils import generate_otp, send_otp_email, is_otp_valid


# ──────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────

def get_tokens_for_student(student):
    """Generate JWT access + refresh token pair for a student."""
    refresh = RefreshToken.for_user(student)
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }


# ──────────────────────────────────────────────
# Frontend Page Views  (render HTML templates)
# ──────────────────────────────────────────────

def register_page(request):
    """Render student registration page."""
    return render(request, 'student_auth/register.html')


def login_page(request):
    """Render student login page."""
    return render(request, 'student_auth/login.html')


def profile_page(request):
    """Render student profile page."""
    return render(request, 'student_auth/profile.html')


# ──────────────────────────────────────────────
# API Views  (return JSON responses)
# ──────────────────────────────────────────────

class StudentRegisterView(APIView):
    """
    POST /api/auth/register/
    Register a new student. No authentication required.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StudentRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.save()
            tokens  = get_tokens_for_student(student)
            return Response(
                {
                    'message': 'Registration successful!',
                    'student': {
                        'id':    student.id,
                        'name':  student.name,
                        'email': student.email,
                    },
                    'tokens': tokens,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentLoginView(APIView):
    """
    POST /api/auth/login/
    Login with email + password. Returns JWT tokens on success.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StudentLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email    = serializer.validated_data['email']
        password = serializer.validated_data['password']

        student = authenticate(request, username=email, password=password)
        if student is None:
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not student.is_active:
            return Response(
                {'error': 'Account is inactive. Please contact support.'},
                status=status.HTTP_403_FORBIDDEN
            )

        tokens = get_tokens_for_student(student)
        return Response(
            {
                'message': 'Login successful!',
                'student': {
                    'id':    student.id,
                    'name':  student.name,
                    'email': student.email,
                },
                'tokens': tokens,
            },
            status=status.HTTP_200_OK
        )


class OTPRequestView(APIView):
    """
    POST /api/auth/otp/request/
    Send a 6-digit OTP to the student's registered email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']

        try:
            student = Student.objects.get(email=email)
        except Student.DoesNotExist:
            # Do not reveal whether email exists (security)
            return Response(
                {'message': 'If this email is registered, an OTP has been sent.'},
                status=status.HTTP_200_OK
            )

        # Invalidate all previous unused OTPs
        OTPRecord.objects.filter(student=student, is_used=False).update(is_used=True)

        # Generate and save new OTP
        otp_code = generate_otp()
        OTPRecord.objects.create(student=student, otp_code=otp_code)

        # Send OTP email
        send_otp_email(student.email, otp_code, student.name)

        return Response(
            {'message': 'If this email is registered, an OTP has been sent.'},
            status=status.HTTP_200_OK
        )


class OTPVerifyView(APIView):
    """
    POST /api/auth/otp/verify/
    Verify OTP code. Returns JWT tokens on success.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email    = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']

        try:
            student = Student.objects.get(email=email)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Invalid email or OTP.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        otp_record = (
            OTPRecord.objects
            .filter(student=student, otp_code=otp_code, is_used=False)
            .order_by('-created_at')
            .first()
        )

        if otp_record is None or not is_otp_valid(otp_record):
            return Response(
                {'error': 'Invalid or expired OTP. Please request a new one.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Mark OTP as used (single-use only)
        otp_record.is_used = True
        otp_record.save()

        tokens = get_tokens_for_student(student)
        return Response(
            {
                'message': 'OTP verified. Login successful!',
                'student': {
                    'id':    student.id,
                    'name':  student.name,
                    'email': student.email,
                },
                'tokens': tokens,
            },
            status=status.HTTP_200_OK
        )


class StudentLogoutView(APIView):
    """
    POST /api/auth/logout/
    Blacklist the refresh token to invalidate it. Requires valid JWT.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required for logout.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)


class StudentProfileView(APIView):
    """
    GET /api/auth/profile/
    Retrieve authenticated student's full profile.
    Requires: Authorization: Bearer <access_token>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = StudentProfileSerializer(request.user)
        return Response(
            {
                'message': 'Profile retrieved successfully.',
                'student': serializer.data,
            },
            status=status.HTTP_200_OK
        )
