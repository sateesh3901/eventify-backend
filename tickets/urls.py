from django.urls import path
from . import views

# All ticket-related routes
# Base: /api/tickets/

urlpatterns = [
    # ── Purchase ─────────────────────────────────────
    path('purchase/<int:event_id>/',      views.purchase_ticket_view,     name='ticket-purchase'),

    # ── Payment ──────────────────────────────────────
    path('payment/create-order/',         views.create_payment_order_view, name='payment-create-order'),
    path('payment/verify/',               views.verify_payment_view,       name='payment-verify'),
    path('payment/status/<int:ticket_id>/', views.payment_status_view,    name='payment-status'),

    # ── Scan (must be BEFORE <str:ticket_code>/) ─────
    path('scan/',                         views.scan_ticket_view,          name='ticket-scan'),

    # ── Host View ────────────────────────────────────
    path('event/<int:event_id>/',         views.event_tickets_view,        name='event-tickets'),

    # ── My Tickets & Detail ──────────────────────────
    path('my-tickets/',                   views.my_tickets_view,           name='my-tickets'),
    path('<str:ticket_code>/',            views.ticket_detail_view,        name='ticket-detail'),
]