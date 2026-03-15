from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Student


class StudentRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for student registration with all 8 required fields."""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model  = Student
        fields = [
            'name', 'email', 'contact_no', 'address',
            'school_college_name', 'course_selection',
            'password', 'confirm_password', 'terms_conditions_accepted',
        ]

    def validate_terms_conditions_accepted(self, value):
        if not value:
            raise serializers.ValidationError(
                'You must accept the terms and conditions to register.'
            )
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        student = Student(**validated_data)
        student.set_password(password)   # hashes the password
        student.save()
        return student


class StudentLoginSerializer(serializers.Serializer):
    """Serializer for email + password login."""

    email    = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class OTPRequestSerializer(serializers.Serializer):
    """Serializer for requesting an OTP via email."""

    email = serializers.EmailField(required=True)


class OTPVerifySerializer(serializers.Serializer):
    """Serializer for verifying OTP code."""

    email    = serializers.EmailField(required=True)
    otp_code = serializers.CharField(required=True, min_length=6, max_length=6)


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for reading student profile. Returns all student information."""

    class Meta:
        model  = Student
        fields = [
            'id', 'name', 'email', 'contact_no', 'address',
            'school_college_name', 'course_selection',
            'terms_conditions_accepted', 'date_joined',
        ]
        read_only_fields = fields
