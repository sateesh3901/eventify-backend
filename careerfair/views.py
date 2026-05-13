from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import JobOpening, JobApplication
from .serializers import (
    JobOpeningSerializer,
    JobOpeningCreateSerializer,
    JobApplicationSerializer,
    JobApplicationCreateSerializer,
)
from tickets.models import Ticket


# ══════════════════════════════════════════════════════════════════
# JOB OPENINGS
# ══════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def job_openings_list_view(request, event_id):
    """
    List all job openings for a career fair event.
    GET /api/careerfair/events/<event_id>/jobs/
    """
    jobs = JobOpening.objects.filter(
        event_id=event_id,
        is_active=True
    )

    # ── Optional filters ─────────────────────────────────────
    experience  = request.query_params.get('experience')
    job_type    = request.query_params.get('job_type')
    search      = request.query_params.get('search')

    if experience:
        jobs = jobs.filter(experience=experience)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if search:
        jobs = jobs.filter(
            job_title__icontains=search
        ) | jobs.filter(
            company_name__icontains=search
        ) | jobs.filter(
            skills_required__icontains=search
        )

    serializer = JobOpeningSerializer(jobs, many=True)
    return Response({
        'count' : jobs.count(),
        'jobs'  : serializer.data,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def job_opening_create_view(request):
    """
    Create a job opening inside a career fair event.
    Hosts only.
    POST /api/careerfair/jobs/create/
    """
    if request.user.role != 'host':
        return Response({
            'message': 'Only Hosts can post job openings.'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = JobOpeningCreateSerializer(data=request.data)

    if serializer.is_valid():
        job = serializer.save(posted_by=request.user)
        return Response({
            'message' : f'Job opening "{job.job_title}" at {job.company_name} posted!',
            'job'     : JobOpeningSerializer(job).data,
        }, status=status.HTTP_201_CREATED)

    return Response({
        'message' : 'Failed to create job opening.',
        'errors'  : serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def job_opening_detail_view(request, job_id):
    """
    Get a single job opening details.
    GET /api/careerfair/jobs/<job_id>/
    """
    try:
        job = JobOpening.objects.get(pk=job_id, is_active=True)
    except JobOpening.DoesNotExist:
        return Response({
            'message': 'Job opening not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'job': JobOpeningSerializer(job).data
    }, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def job_opening_update_view(request, job_id):
    """
    Update a job opening. Host owner only.
    PUT/PATCH /api/careerfair/jobs/<job_id>/update/
    """
    try:
        job = JobOpening.objects.get(pk=job_id, posted_by=request.user)
    except JobOpening.DoesNotExist:
        return Response({
            'message': 'Job opening not found or not yours.'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = JobOpeningCreateSerializer(
        job,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        job = serializer.save()
        return Response({
            'message' : f'Job opening "{job.job_title}" updated!',
            'job'     : JobOpeningSerializer(job).data,
        }, status=status.HTTP_200_OK)

    return Response({
        'message' : 'Update failed.',
        'errors'  : serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def job_opening_delete_view(request, job_id):
    """
    Delete a job opening. Host owner only.
    DELETE /api/careerfair/jobs/<job_id>/delete/
    """
    try:
        job = JobOpening.objects.get(pk=job_id, posted_by=request.user)
    except JobOpening.DoesNotExist:
        return Response({
            'message': 'Job opening not found or not yours.'
        }, status=status.HTTP_404_NOT_FOUND)

    title = job.job_title
    job.delete()

    return Response({
        'message': f'Job opening "{title}" deleted successfully!'
    }, status=status.HTTP_200_OK)


# ══════════════════════════════════════════════════════════════════
# JOB APPLICATIONS
# ══════════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_for_job_view(request, job_id):
    """
    Apply for a job opening at a career fair.
    User must have a valid ticket for the event.
    POST /api/careerfair/jobs/<job_id>/apply/
    """

    # ── Get job ──────────────────────────────────────────────
    try:
        job = JobOpening.objects.get(pk=job_id, is_active=True)
    except JobOpening.DoesNotExist:
        return Response({
            'message': 'Job opening not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    # ── Must have valid ticket for this event ─────────────────
    has_ticket = Ticket.objects.filter(
        event   = job.event,
        user    = request.user,
        payment_status__in = ['completed', 'free']
    ).exists()

    if not has_ticket:
        return Response({
            'message': 'You must have a valid ticket for this event to apply.'
        }, status=status.HTTP_403_FORBIDDEN)

    # ── Check already applied ────────────────────────────────
    if JobApplication.objects.filter(
        job=job,
        applicant=request.user
    ).exists():
        return Response({
            'message': 'You have already applied for this job!'
        }, status=status.HTTP_400_BAD_REQUEST)

    # ── Create application ───────────────────────────────────
    serializer = JobApplicationCreateSerializer(data=request.data)

    if serializer.is_valid():
        application = serializer.save(
            job       = job,
            applicant = request.user,
        )
        return Response({
            'message'     : f'Successfully applied for "{job.job_title}" at {job.company_name}!',
            'application' : JobApplicationSerializer(application).data,
        }, status=status.HTTP_201_CREATED)

    return Response({
        'message' : 'Application failed.',
        'errors'  : serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_applications_view(request):
    """
    Get all job applications by the logged-in user.
    GET /api/careerfair/my-applications/
    """
    applications = JobApplication.objects.filter(applicant=request.user)
    serializer   = JobApplicationSerializer(applications, many=True)

    return Response({
        'count'        : applications.count(),
        'applications' : serializer.data,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_applications_list_view(request, job_id):
    """
    Get all applications for a job opening.
    Host only — to review candidates.
    GET /api/careerfair/jobs/<job_id>/applications/
    """
    if request.user.role != 'host':
        return Response({
            'message': 'Only Hosts can view applications.'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        job = JobOpening.objects.get(pk=job_id, posted_by=request.user)
    except JobOpening.DoesNotExist:
        return Response({
            'message': 'Job opening not found or not yours.'
        }, status=status.HTTP_404_NOT_FOUND)

    applications = JobApplication.objects.filter(job=job)
    serializer   = JobApplicationSerializer(applications, many=True)

    return Response({
        'job'          : job.job_title,
        'company'      : job.company_name,
        'count'        : applications.count(),
        'applications' : serializer.data,
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_application_status_view(request, application_id):
    """
    Update application status (shortlist, reject, select).
    Host only.
    PATCH /api/careerfair/applications/<application_id>/status/
    """
    if request.user.role != 'host':
        return Response({
            'message': 'Only Hosts can update application status.'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        application = JobApplication.objects.get(
            pk         = application_id,
            job__posted_by = request.user
        )
    except JobApplication.DoesNotExist:
        return Response({
            'message': 'Application not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    valid_statuses = ['applied', 'reviewed', 'shortlisted', 'rejected', 'selected']

    if new_status not in valid_statuses:
        return Response({
            'message' : f'Invalid status. Choose from: {valid_statuses}'
        }, status=status.HTTP_400_BAD_REQUEST)

    application.status = new_status
    application.save()

    return Response({
        'message'    : f'Application status updated to "{new_status}"!',
        'applicant'  : application.applicant.username,
        'job'        : application.job.job_title,
        'new_status' : new_status,
    }, status=status.HTTP_200_OK)