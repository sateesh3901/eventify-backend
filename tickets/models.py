from django.db import models
from accounts.models import CustomUser
from events.models import Event
import uuid


class Ticket(models.Model):
    """
    Represents a purchased ticket for an event.
    Each ticket has a unique QR code for entry validation.
    """

    STATUS_CHOICES = (
        ('active',    'Active'),
        ('scanned',   'Scanned'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending',   'Pending'),
        ('completed', 'Completed'),
        ('failed',    'Failed'),
        ('free',      'Free'),
    )

    # ── Relations ────────────────────────────────────────────
    event           = models.ForeignKey(
                        Event,
                        on_delete=models.CASCADE,
                        related_name='tickets'
                      )
    user            = models.ForeignKey(
                        CustomUser,
                        on_delete=models.CASCADE,
                        related_name='tickets'
                      )

    # ── Ticket Identity ──────────────────────────────────────
    ticket_code     = models.UUIDField(
                        default=uuid.uuid4,
                        unique=True,
                        editable=False
                      )
    qr_code         = models.ImageField(
                        upload_to='qrcodes/',
                        blank=True,
                        null=True
                      )

    # ── Status ───────────────────────────────────────────────
    status          = models.CharField(
                        max_length=20,
                        choices=STATUS_CHOICES,
                        default='active'
                      )

    # ── Payment ──────────────────────────────────────────────
    payment_status  = models.CharField(
                        max_length=20,
                        choices=PAYMENT_STATUS_CHOICES,
                        default='pending'
                      )
    amount_paid     = models.DecimalField(
                        max_digits=8,
                        decimal_places=2,
                        default=0.00
                      )
    razorpay_order_id   = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)

    # ── Scan Info ────────────────────────────────────────────
    scanned_at      = models.DateTimeField(blank=True, null=True)
    scanned_by      = models.ForeignKey(
                        CustomUser,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='scanned_tickets'
                      )

    # ── Meta ─────────────────────────────────────────────────
    purchased_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table            = 'eventify_tickets'
        verbose_name        = 'Ticket'
        verbose_name_plural = 'Tickets'
        # One ticket per user per event
        unique_together     = ['event', 'user']

    def __str__(self):
        return f"Ticket {self.ticket_code} | {self.user.username} → {self.event.title}"

    @property
    def is_valid(self):
        return (
            self.status == 'active' and
            self.payment_status in ['completed', 'free']  # ✅ already correct
        )


class ScanLog(models.Model):
    """
    Logs every QR code scan attempt for audit trail.
    """

    ticket      = models.ForeignKey(
                    Ticket,
                    on_delete=models.CASCADE,
                    related_name='scan_logs'
                  )
    scanned_by  = models.ForeignKey(
                    CustomUser,
                    on_delete=models.SET_NULL,
                    null=True,
                    related_name='scan_logs'
                  )
    scanned_at  = models.DateTimeField(auto_now_add=True)
    was_valid   = models.BooleanField(default=True)
    notes       = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table  = 'eventify_scan_logs'
        ordering  = ['-scanned_at']

    def __str__(self):
        return f"Scan by {self.scanned_by} at {self.scanned_at}"