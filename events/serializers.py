from rest_framework import serializers
from .models import Event
from accounts.serializers import UserSerializer


class EventSerializer(serializers.ModelSerializer):
    """
    Full serializer for Event model.
    Includes host details and computed ticket stats.
    """

    # Read-only computed fields
    host            = UserSerializer(read_only=True)
    tickets_sold    = serializers.IntegerField(read_only=True)
    tickets_remaining = serializers.IntegerField(read_only=True)
    is_sold_out     = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Event
        fields = [
            'id', 'title', 'description', 'event_type',
            'status', 'date_time', 'venue', 'city',
            'ticket_limit', 'ticket_price', 'host',
            'banner_image', 'is_active', 'tickets_sold',
            'tickets_remaining', 'is_sold_out',
            'created_at', 'updated_at',
        ]


class EventCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating events.
    Host is automatically set from request user.
    """

    class Meta:
        model  = Event
        fields = [
            'title', 'description', 'event_type',
            'status', 'date_time', 'venue', 'city',
            'ticket_limit', 'ticket_price', 'banner_image',
        ]

    def validate_ticket_limit(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Ticket limit must be at least 1.'
            )
        return value

    def validate_ticket_price(self, value):
        if value < 0:
            raise serializers.ValidationError(
                'Ticket price cannot be negative.'
            )
        return value