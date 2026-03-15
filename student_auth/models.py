import re
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError


def validate_phone_number(value):
    """Validate phone number format."""
    pattern = re.compile(r'^\+?[1-9]\d{9,14}$')
    if not pattern.match(value):
        raise ValidationError(
            'Enter a valid phone number. Example: +919876543210 or 9876543210'
        )


class StudentManager(BaseUserManager):
    """Custom manager for Student model."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('name', 'Admin')
        extra_fields.setdefault('contact_no', '9999999999')
        extra_fields.setdefault('address', 'Admin Address')
        extra_fields.setdefault('school_college_name', 'Admin')
        extra_fields.setdefault('course_selection', 'Admin')
        extra_fields.setdefault('terms_conditions_accepted', True)
        return self.create_user(email, password, **extra_fields)


class Student(AbstractBaseUser, PermissionsMixin):
    """
    Custom Student model using email as the unique identifier.
    All 8 fields as per CareerWale task specification.
    """

    name                      = models.CharField(max_length=150)
    email                     = models.EmailField(unique=True, validators=[EmailValidator()])
    contact_no                = models.CharField(max_length=15, validators=[validate_phone_number])
    address                   = models.TextField()
    school_college_name       = models.CharField(max_length=255)
    course_selection          = models.CharField(max_length=255)
    terms_conditions_accepted = models.BooleanField(default=False)

    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = StudentManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name        = 'Student'
        verbose_name_plural = 'Students'
        ordering            = ['-date_joined']

    def __str__(self):
        return f'{self.name} <{self.email}>'


class OTPRecord(models.Model):
    """Stores OTP codes for email-based login. Valid for 5 minutes, single use."""

    student    = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='otp_records')
    otp_code   = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used    = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'OTP for {self.student.email}'
