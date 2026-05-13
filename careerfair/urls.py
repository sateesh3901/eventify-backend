from django.urls import path
from . import views

# All career fair related routes
# Base: /api/careerfair/

urlpatterns = [

    # ── Job Openings ─────────────────────────────────
    path('events/<int:event_id>/jobs/',   views.job_openings_list_view,    name='job-list'),
    path('jobs/create/',                  views.job_opening_create_view,   name='job-create'),
    path('jobs/<int:job_id>/',            views.job_opening_detail_view,   name='job-detail'),
    path('jobs/<int:job_id>/update/',     views.job_opening_update_view,   name='job-update'),
    path('jobs/<int:job_id>/delete/',     views.job_opening_delete_view,   name='job-delete'),

    # ── Job Applications ─────────────────────────────
    path('jobs/<int:job_id>/apply/',          views.apply_for_job_view,            name='job-apply'),
    path('jobs/<int:job_id>/applications/',   views.job_applications_list_view,    name='job-applications'),
    path('my-applications/',                  views.my_applications_view,          name='my-applications'),
    path('applications/<int:application_id>/status/', views.update_application_status_view, name='application-status'),
]