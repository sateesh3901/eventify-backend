from django.db import models
from accounts.models import CustomUser


class Event(models.Model):
    """
    Represents an event created by a Host.
    Can be a general event or a career fair.
    """

    EVENT_TYPE_CHOICES = (
        ('general',     'General Event'),
        ('career_fair', 'Career Fair'),
        ('concert',     'Concert'),
        ('workshop',    'Workshop'),
        ('conference',  'Conference'),
        ('hackathon',   'Hackathon'),
    )

    STATUS_CHOICES = (
        ('upcoming',   'Upcoming'),
        ('ongoing',    'Ongoing'),
        ('completed',  'Completed'),
        ('cancelled',  'Cancelled'),
    )

    # ── Basic Info ───────────────────────────────────────────
    title           = models.CharField(max_length=200)
    description     = models.TextField()
    event_type      = models.CharField(
                        max_length=20,
                        choices=EVENT_TYPE_CHOICES,
                        default='general'
                      )
    status          = models.CharField(
                        max_length=20,
                        choices=STATUS_CHOICES,
                        default='upcoming'
                      )

    # ── Date & Location ──────────────────────────────────────
    date_time       = models.DateTimeField()
    venue           = models.CharField(max_length=300)
    city            = models.CharField(max_length=100)

    # ── Ticket Info ──────────────────────────────────────────
    ticket_limit    = models.PositiveIntegerField()
    ticket_price    = models.DecimalField(
                        max_digits=8,
                        decimal_places=2,
                        default=0.00
                      )

    # ── Relations ────────────────────────────────────────────
    host            = models.ForeignKey(
                        CustomUser,
                        on_delete=models.CASCADE,
                        related_name='hosted_events'
                      )

    # ── Meta ─────────────────────────────────────────────────
    banner_image    = models.ImageField(
                        upload_to='event_banners/',
                        blank=True,
                        null=True
                      )
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table  = 'eventify_events'
        ordering  = ['-date_time']
        verbose_name        = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return f"{self.title} ({self.event_type}) by {self.host.username}"

    @property
    def tickets_sold(self):
        return self.tickets.count()

    @property
    def tickets_remaining(self):
        return self.ticket_limit - self.tickets.count()

    @property
    def is_sold_out(self):
        return self.tickets.count() >= self.ticket_limit