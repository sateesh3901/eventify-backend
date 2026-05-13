from rest_framework import serializers
from .models import Ticket, ScanLog
from accounts.serializers import UserSerializer
from events.serializers import EventSerializer


class TicketSerializer(serializers.ModelSerializer):
    """
    Full ticket serializer with event and user details.
    """
    user        = UserSerializer(read_only=True)
    event       = EventSerializer(read_only=True)
    is_valid    = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Ticket
        fields = [
            'id', 'ticket_code', 'qr_code',
            'event', 'user', 'status',
            'payment_status', 'amount_paid',
            'razorpay_order_id', 'razorpay_payment_id',
            'is_valid', 'scanned_at', 'purchased_at',
        ]


class ScanLogSerializer(serializers.ModelSerializer):
    """
    Serializer for scan log entries.
    """
    scanned_by = UserSerializer(read_only=True)

    class Meta:
        model  = ScanLog
        fields = ['id', 'ticket', 'scanned_by', 'scanned_at', 'was_valid', 'notes']