from django.urls import path
from . import views

# All stats routes
# Base: /api/stats/

urlpatterns = [

    # ── Host Stats ───────────────────────────────────
    path('host/dashboard/',             views.host_dashboard_stats_view,  name='host-dashboard-stats'),
    path('host/events/<int:event_id>/', views.host_event_stats_view,      name='host-event-stats'),

    # ── User Stats ───────────────────────────────────
    path('user/dashboard/',             views.user_dashboard_stats_view,  name='user-dashboard-stats'),

    # ── Admin Stats ──────────────────────────────────
    path('admin/dashboard/',            views.admin_dashboard_stats_view, name='admin-dashboard-stats'),
]