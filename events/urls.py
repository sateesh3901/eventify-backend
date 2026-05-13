from django.urls import path
from . import views

# All event-related routes
# Base: /api/events/

urlpatterns = [
    # ── Public Routes ────────────────────────────────
    path('',              views.event_list_view,   name='event-list'),
    path('<int:pk>/',     views.event_detail_view, name='event-detail'),

    # ── Host Only Routes ─────────────────────────────
    path('create/',             views.event_create_view, name='event-create'),
    path('<int:pk>/update/',    views.event_update_view, name='event-update'),
    path('<int:pk>/delete/',    views.event_delete_view, name='event-delete'),
    path('my-events/',          views.host_events_view,  name='host-events'),
]