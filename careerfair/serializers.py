from rest_framework import serializers
from .models import JobOpening, JobApplication
from accounts.serializers import UserSerializer


class JobOpeningSerializer(serializers.ModelSerializer):
    """
    Serializer for reading job openings.
    Includes host details and application count.
    """
    posted_by           = UserSerializer(read_only=True)
    total_applications  = serializers.IntegerField(read_only=True)

    class Meta:
        model  = JobOpening
        fields = [
            'id', 'event', 'posted_by',
            'company_name', 'company_website', 'company_logo',
            'job_title', 'job_type', 'experience',
            'description', 'skills_required',
            'salary_range', 'openings_count',
            'total_applications', 'is_active', 'created_at',
        ]


class JobOpeningCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating job openings.
    Host only.
    """

    class Meta:
        model  = JobOpening
        fields = [
            'event', 'company_name', 'company_website',
            'company_logo', 'job_title', 'job_type',
            'experience', 'description', 'skills_required',
            'salary_range', 'openings_count',
        ]

    def validate_event(self, event):
        # Only career fair events allowed
        if event.event_type != 'career_fair':
            raise serializers.ValidationError(
                'Job openings can only be added to Career Fair events.'
            )
        return event


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for reading job applications.
    """
    applicant   = UserSerializer(read_only=True)
    job_title   = serializers.CharField(source='job.job_title', read_only=True)
    company     = serializers.CharField(source='job.company_name', read_only=True)

    class Meta:
        model  = JobApplication
        fields = [
            'id', 'job', 'job_title', 'company',
            'applicant', 'resume', 'cover_letter',
            'status', 'portfolio_url', 'github_url',
            'linkedin_url', 'applied_at', 'updated_at',
        ]


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for submitting a job application.
    """

    class Meta:
        model  = JobApplication
        fields = [
            'resume', 'cover_letter',
            'portfolio_url', 'github_url', 'linkedin_url',
        ]