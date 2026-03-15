from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Student, OTPRecord


@admin.register(Student)
class StudentAdmin(UserAdmin):
    list_display  = ['name', 'email', 'contact_no', 'course_selection', 'is_active', 'date_joined']
    list_filter   = ['is_active', 'course_selection']
    search_fields = ['name', 'email', 'contact_no']
    ordering      = ['-date_joined']

    fieldsets = (
        (None,          {'fields': ('email', 'password')}),
        ('Personal',    {'fields': ('name', 'contact_no', 'address')}),
        ('Academic',    {'fields': ('school_college_name', 'course_selection')}),
        ('Agreement',   {'fields': ('terms_conditions_accepted',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Dates',       {'fields': ('date_joined', 'last_login')}),
    )
    readonly_fields = ['date_joined', 'last_login']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'contact_no', 'address',
                'school_college_name', 'course_selection',
                'terms_conditions_accepted', 'password1', 'password2'
            ),
        }),
    )


@admin.register(OTPRecord)
class OTPRecordAdmin(admin.ModelAdmin):
    list_display  = ['student', 'otp_code', 'created_at', 'is_used']
    list_filter   = ['is_used']
    search_fields = ['student__email']
    readonly_fields = ['created_at']
