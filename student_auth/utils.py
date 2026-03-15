import random
import string
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


def generate_otp(length=6):
    """Generate a random 6-digit numeric OTP."""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(email, otp_code, student_name):
    """
    Send OTP to student email.
    In development: prints to console.
    In production: configure SMTP in settings.py.
    """
    subject = 'Your Physics Wallah Login OTP'
    message = (
        f'Hello {student_name},\n\n'
        f'Your One-Time Password (OTP) for Physics Wallah login is:\n\n'
        f'    {otp_code}\n\n'
        f'This OTP is valid for 5 minutes. Do not share it with anyone.\n\n'
        f'Regards,\nCareerWale Team'
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def is_otp_valid(otp_record):
    """Check if OTP is unused and within 5-minute expiry window."""
    expiry_seconds = getattr(settings, 'OTP_EXPIRY_SECONDS', 300)
    expiry_time = otp_record.created_at + timedelta(seconds=expiry_seconds)
    return (not otp_record.is_used) and (timezone.now() <= expiry_time)
