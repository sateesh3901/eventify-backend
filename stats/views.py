from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.utils import timezone

from events.models import Event
from tickets.models import Ticket, ScanLog
from careerfair.models import JobOpening, JobApplication
from accounts.models import CustomUser


# ══════════════════════════════════════════════════════════════════
# HOST STATS
# ══════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def host_dashboard_stats_view(request):
    """
    Complete stats for a Host's dashboard.
    GET /api/stats/host/dashboard/
    """
    if request.user.role != 'host':
        return Response({
            'message': 'Only Hosts can access this.'
        }, status=status.HTTP_403_FORBIDDEN)

    # ── Event Stats ──────────────────────────────────────────
    my_events       = Event.objects.filter(host=request.user)
    total_events    = my_events.count()
    upcoming_events = my_events.filter(status='upcoming').count()
    ongoing_events  = my_events.filter(status='ongoing').count()
    completed_events= my_events.filter(status='completed').count()

    # ── Ticket Stats ─────────────────────────────────────────
    my_event_ids    = my_events.values_list('id', flat=True)
    total_tickets   = Ticket.objects.filter(event_id__in=my_event_ids)
    tickets_sold    = total_tickets.count()
    tickets_scanned = total_tickets.filter(status='scanned').count()
    free_tickets    = total_tickets.filter(payment_status='free').count()
    paid_tickets    = total_tickets.filter(payment_status='completed').count()

    # ── Revenue Stats ────────────────────────────────────────
    total_revenue   = total_tickets.filter(
                        payment_status='completed'
                      ).aggregate(
                        total=Sum('amount_paid')
                      )['total'] or 0

    # ── Career Fair Stats ────────────────────────────────────
    total_job_openings  = JobOpening.objects.filter(
                            posted_by=request.user
                          ).count()
    total_applications  = JobApplication.objects.filter(
                            job__posted_by=request.user
                          ).count()
    shortlisted         = JobApplication.objects.filter(
                            job__posted_by=request.user,
                            status='shortlisted'
                          ).count()
    selected            = JobApplication.objects.filter(
                            job__posted_by=request.user,
                            status='selected'
                          ).count()

    # ── Per Event Breakdown ──────────────────────────────────
    event_breakdown = []
    for event in my_events:
        event_tickets = Ticket.objects.filter(event=event)
        event_breakdown.append({
            'event_id'       : event.id,
            'event_title'    : event.title,
            'event_type'     : event.event_type,
            'status'         : event.status,
            'ticket_limit'   : event.ticket_limit,
            'tickets_sold'   : event_tickets.count(),
            'tickets_scanned': event_tickets.filter(status='scanned').count(),
            'tickets_remaining': event.tickets_remaining,
            'revenue'        : float(
                                event_tickets.filter(
                                    payment_status='completed'
                                ).aggregate(
                                    total=Sum('amount_paid')
                                )['total'] or 0
                               ),
        })

    return Response({
        'host'              : request.user.username,
        'summary': {
            'total_events'      : total_events,
            'upcoming_events'   : upcoming_events,
            'ongoing_events'    : ongoing_events,
            'completed_events'  : completed_events,
            'tickets_sold'      : tickets_sold,
            'tickets_scanned'   : tickets_scanned,
            'free_tickets'      : free_tickets,
            'paid_tickets'      : paid_tickets,
            'total_revenue'     : f'₹{total_revenue}',
            'job_openings'      : total_job_openings,
            'total_applications': total_applications,
            'shortlisted'       : shortlisted,
            'selected'          : selected,
        },
        'event_breakdown'   : event_breakdown,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def host_event_stats_view(request, event_id):
    """
    Detailed stats for a single event.
    Host only.
    GET /api/stats/host/events/<event_id>/
    """
    if request.user.role != 'host':
        return Response({
            'message': 'Only Hosts can access this.'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        event = Event.objects.get(pk=event_id, host=request.user)
    except Event.DoesNotExist:
        return Response({
            'message': 'Event not found or not yours.'
        }, status=status.HTTP_404_NOT_FOUND)

    # ── Ticket Stats ─────────────────────────────────────────
    tickets         = Ticket.objects.filter(event=event)
    tickets_sold    = tickets.count()
    tickets_scanned = tickets.filter(status='scanned').count()
    tickets_active  = tickets.filter(status='active').count()

    # ── Revenue ──────────────────────────────────────────────
    revenue = tickets.filter(
                payment_status='completed'
              ).aggregate(
                total=Sum('amount_paid')
              )['total'] or 0

    # ── Recent Scans ─────────────────────────────────────────
    recent_scans = ScanLog.objects.filter(
                    ticket__event=event
                   ).order_by('-scanned_at')[:10]

    recent_scan_data = [{
        'attendee'  : scan.ticket.user.username,
        'scanned_at': scan.scanned_at,
        'was_valid' : scan.was_valid,
    } for scan in recent_scans]

    # ── Career Fair specific ─────────────────────────────────
    career_fair_data = None
    if event.event_type == 'career_fair':
        jobs = JobOpening.objects.filter(event=event)
        career_fair_data = {
            'total_jobs'        : jobs.count(),
            'total_applications': JobApplication.objects.filter(
                                    job__event=event
                                  ).count(),
            'shortlisted'       : JobApplication.objects.filter(
                                    job__event=event,
                                    status='shortlisted'
                                  ).count(),
            'selected'          : JobApplication.objects.filter(
                                    job__event=event,
                                    status='selected'
                                  ).count(),
            'jobs_breakdown'    : [{
                'job_title'     : job.job_title,
                'company'       : job.company_name,
                'applications'  : job.total_applications,
                'openings'      : job.openings_count,
            } for job in jobs],
        }

    return Response({
        'event'         : event.title,
        'event_type'    : event.event_type,
        'status'        : event.status,
        'date_time'     : event.date_time,
        'venue'         : event.venue,
        'ticket_stats': {
            'limit'     : event.ticket_limit,
            'sold'      : tickets_sold,
            'scanned'   : tickets_scanned,
            'active'    : tickets_active,
            'remaining' : event.tickets_remaining,
            'sold_out'  : event.is_sold_out,
        },
        'revenue'       : f'₹{revenue}',
        'recent_scans'  : recent_scan_data,
        'career_fair'   : career_fair_data,
    }, status=status.HTTP_200_OK)


# ══════════════════════════════════════════════════════════════════
# USER STATS
# ══════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard_stats_view(request):
    """
    Stats for a regular user's dashboard.
    GET /api/stats/user/dashboard/
    """
    tickets         = Ticket.objects.filter(user=request.user)
    applications    = JobApplication.objects.filter(applicant=request.user)

    # ── Upcoming events ──────────────────────────────────────
    upcoming = tickets.filter(
                event__status='upcoming',
                status='active'
               ).count()

    return Response({
        'user'  : request.user.username,
        'stats' : {
            'total_tickets'     : tickets.count(),
            'upcoming_events'   : upcoming,
            'attended_events'   : tickets.filter(status='scanned').count(),
            'total_applications': applications.count(),
            'shortlisted'       : applications.filter(status='shortlisted').count(),
            'selected'          : applications.filter(status='selected').count(),
            'rejected'          : applications.filter(status='rejected').count(),
        },
        'recent_tickets': [{
            'event'         : t.event.title,
            'event_type'    : t.event.event_type,
            'date'          : t.event.date_time,
            'ticket_code'   : str(t.ticket_code),
            'status'        : t.status,
            'payment_status': t.payment_status,
        } for t in tickets.order_by('-purchased_at')[:5]],
        'recent_applications': [{
            'job_title' : a.job.job_title,
            'company'   : a.job.company_name,
            'status'    : a.status,
            'applied_at': a.applied_at,
        } for a in applications.order_by('-applied_at')[:5]],
    }, status=status.HTTP_200_OK)


# ══════════════════════════════════════════════════════════════════
# ADMIN STATS
# ══════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_stats_view(request):
    """
    Platform-wide stats for Admin dashboard.
    GET /api/stats/admin/dashboard/
    """
    if request.user.role != 'admin':
        return Response({
            'message': 'Only Admins can access this.'
        }, status=status.HTTP_403_FORBIDDEN)

    # ── Platform Stats ───────────────────────────────────────
    total_users     = CustomUser.objects.filter(role='user').count()
    total_hosts     = CustomUser.objects.filter(role='host').count()
    total_admins    = CustomUser.objects.filter(role='admin').count()
    total_events    = Event.objects.count()
    active_events   = Event.objects.filter(is_active=True).count()
    total_tickets   = Ticket.objects.count()
    total_revenue   = Ticket.objects.filter(
                        payment_status='completed'
                      ).aggregate(
                        total=Sum('amount_paid')
                      )['total'] or 0
    total_jobs      = JobOpening.objects.count()
    total_apps      = JobApplication.objects.count()

    # ── Top Events by Tickets ────────────────────────────────
    top_events = Event.objects.annotate(
                    ticket_count=Count('tickets')
                 ).order_by('-ticket_count')[:5]

    return Response({
        'platform_summary': {
            'total_users'       : total_users,
            'total_hosts'       : total_hosts,
            'total_admins'      : total_admins,
            'total_events'      : total_events,
            'active_events'     : active_events,
            'total_tickets_sold': total_tickets,
            'total_revenue'     : f'₹{total_revenue}',
            'total_job_openings': total_jobs,
            'total_applications': total_apps,
        },
        'top_events': [{
            'event_id'      : e.id,
            'title'         : e.title,
            'event_type'    : e.event_type,
            'host'          : e.host.username,
            'tickets_sold'  : e.ticket_count,
            'ticket_limit'  : e.ticket_limit,
        } for e in top_events],
    }, status=status.HTTP_200_OK)