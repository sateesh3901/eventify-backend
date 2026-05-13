from django.contrib import admin
from .models import JobOpening, JobApplication


@admin.register(JobOpening)
class JobOpeningAdmin(admin.ModelAdmin):
    list_display  = [
        'job_title', 'company_name', 'event',
        'job_type', 'experience', 'openings_count',
        'total_applications', 'is_active'
    ]
    list_filter   = ['job_type', 'experience', 'is_active']
    search_fields = ['job_title', 'company_name', 'skills_required']
    ordering      = ['-created_at']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display  = [
        'applicant', 'job', 'status', 'applied_at'
    ]
    list_filter   = ['status']
    search_fields = ['applicant__username', 'job__job_title']
    ordering      = ['-applied_at']