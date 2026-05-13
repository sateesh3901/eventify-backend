from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin panel for Eventify events.
    """
    list_display  = [
        'title', 'event_type', 'status',
        'host', 'city', 'date_time',
        'ticket_limit', 'tickets_sold', 'is_active'
    ]
    list_filter   = ['event_type', 'status', 'city', 'is_active']
    search_fields = ['title', 'host__username', 'city', 'venue']
    ordering      = ['-created_at']