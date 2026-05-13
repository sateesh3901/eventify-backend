from django.db import models
from accounts.models import CustomUser
from events.models import Event


class JobOpening(models.Model):
    """
    A job opening posted by a company inside a Career Fair event.
    Only visible when the event type is 'career_fair'.
    """

    EXPERIENCE_CHOICES = (
        ('fresher',    'Fresher (0-1 years)'),
        ('junior',     'Junior (1-3 years)'),
        ('mid',        'Mid Level (3-5 years)'),
        ('senior',     'Senior (5+ years)'),
    )

    JOB_TYPE_CHOICES = (
        ('full_time',  'Full Time'),
        ('part_time',  'Part Time'),
        ('internship', 'Internship'),
        ('contract',   'Contract'),
    )

    # ── Relations ────────────────────────────────────────────
    event           = models.ForeignKey(
                        Event,
                        on_delete=models.CASCADE,
                        related_name='job_openings'
                      )
    posted_by       = models.ForeignKey(
                        CustomUser,
                        on_delete=models.CASCADE,
                        related_name='job_openings'
                      )

    # ── Company Info ─────────────────────────────────────────
    company_name    = models.CharField(max_length=200)
    company_website = models.URLField(blank=True, null=True)
    company_logo    = models.ImageField(
                        upload_to='company_logos/',
                        blank=True,
                        null=True
                      )

    # ── Job Info ─────────────────────────────────────────────
    job_title       = models.CharField(max_length=200)
    job_type        = models.CharField(
                        max_length=20,
                        choices=JOB_TYPE_CHOICES,
                        default='full_time'
                      )
    experience      = models.CharField(
                        max_length=20,
                        choices=EXPERIENCE_CHOICES,
                        default='fresher'
                      )
    description     = models.TextField()
    skills_required = models.TextField(
                        help_text='Comma separated skills e.g. Python, Django, React'
                      )
    salary_range    = models.CharField(
                        max_length=100,
                        blank=True,
                        null=True,
                        help_text='e.g. ₹3LPA - ₹6LPA'
                      )
    openings_count  = models.PositiveIntegerField(default=1)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table            = 'eventify_job_openings'
        ordering            = ['-created_at']
        verbose_name        = 'Job Opening'
        verbose_name_plural = 'Job Openings'

    def __str__(self):
        return f"{self.job_title} at {self.company_name} — {self.event.title}"

    @property
    def total_applications(self):
        return self.applications.count()


class JobApplication(models.Model):
    """
    A candidate's application to a job opening at a career fair.
    Candidate must have a valid ticket for the event to apply.
    """

    STATUS_CHOICES = (
        ('applied',    'Applied'),
        ('reviewed',   'Reviewed'),
        ('shortlisted','Shortlisted'),
        ('rejected',   'Rejected'),
        ('selected',   'Selected'),
    )

    # ── Relations ────────────────────────────────────────────
    job             = models.ForeignKey(
                        JobOpening,
                        on_delete=models.CASCADE,
                        related_name='applications'
                      )
    applicant       = models.ForeignKey(
                        CustomUser,
                        on_delete=models.CASCADE,
                        related_name='job_applications'
                      )

    # ── Application Details ──────────────────────────────────
    resume          = models.FileField(upload_to='resumes/')
    cover_letter    = models.TextField(blank=True, null=True)
    status          = models.CharField(
                        max_length=20,
                        choices=STATUS_CHOICES,
                        default='applied'
                      )
    portfolio_url   = models.URLField(blank=True, null=True)
    github_url      = models.URLField(blank=True, null=True)
    linkedin_url    = models.URLField(blank=True, null=True)

    # ── Meta ─────────────────────────────────────────────────
    applied_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table            = 'eventify_job_applications'
        ordering            = ['-applied_at']
        verbose_name        = 'Job Application'
        verbose_name_plural = 'Job Applications'
        # One application per job per candidate
        unique_together     = ['job', 'applicant']

    def __str__(self):
        return f"{self.applicant.username} → {self.job.job_title} at {self.job.company_name}"