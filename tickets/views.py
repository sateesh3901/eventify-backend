from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import Ticket, ScanLog
from .serializers import TicketSerializer, ScanLogSerializer
from .utils import generate_qr_code
from events.models import Event


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def purchase_ticket_view(request, event_id):
    """
    Purchase a ticket for an event.
    Free events → ticket issued instantly.
    Paid events → Razorpay order created (next session).
    POST /api/tickets/purchase/<event_id>/
    """

    # ── Get Event ────────────────────────────────────────────
    try:
        event = Event.objects.get(pk=event_id, is_active=True)
    except Event.DoesNotExist:
        return Response({
            'message': 'Event not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    # ── Check already purchased ──────────────────────────────
    if Ticket.objects.filter(event=event, user=request.user).exists():
        return Response({
            'message': 'You already have a ticket for this event!'
        }, status=status.HTTP_400_BAD_REQUEST)

    # ── Check availability ───────────────────────────────────
    if event.is_sold_out:
        return Response({
            'message': 'Sorry! This event is sold out.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # ── Free Event — issue ticket directly ───────────────────
    if event.ticket_price == 0:
        ticket = Ticket.objects.create(
            event          = event,
            user           = request.user,
            payment_status = 'free',
            amount_paid    = 0.00,
        )

        # Generate QR code
        ticket.qr_code = generate_qr_code(ticket.ticket_code, ticket.id)
        ticket.save()

        return Response({
            'message': f'Ticket booked successfully for "{event.title}"!',
            'ticket' : TicketSerializer(ticket).data,
        }, status=status.HTTP_201_CREATED)

    # ── Paid Event — return price info (Razorpay in next session) ──
    return Response({
        'message'       : 'This is a paid event. Proceed to payment.',
        'event_id'      : event.id,
        'event_title'   : event.title,
        'amount'        : float(event.ticket_price),
        'currency'      : 'INR',
        'next_step'     : 'POST /api/tickets/payment/create-order/',
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_tickets_view(request):
    """
    Get all tickets for the logged-in user.
    GET /api/tickets/my-tickets/
    """
    tickets    = Ticket.objects.filter(user=request.user).order_by('-purchased_at')
    serializer = TicketSerializer(tickets, many=True)

    return Response({
        'count'   : tickets.count(),
        'tickets' : serializer.data,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ticket_detail_view(request, ticket_code):
    """
    Get a single ticket by ticket_code.
    GET /api/tickets/<ticket_code>/
    """
    try:
        ticket = Ticket.objects.get(
            ticket_code=ticket_code,
            user=request.user
        )
    except Ticket.DoesNotExist:
        return Response({
            'message': 'Ticket not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'ticket': TicketSerializer(ticket).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scan_ticket_view(request):
    """
    Scan and validate a QR code ticket at event entry.
    Only Hosts can scan tickets.
    POST /api/tickets/scan/
    """

    # ── Host only ────────────────────────────────────────────
    if request.user.role != 'host':
        return Response({
            'message': 'Only Hosts can scan tickets.'
        }, status=status.HTTP_403_FORBIDDEN)

    ticket_code = request.data.get('ticket_code')

    if not ticket_code:
        return Response({
            'message': 'ticket_code is required.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # ── Find ticket ──────────────────────────────────────────
    try:
        ticket = Ticket.objects.get(ticket_code=ticket_code)
    except Ticket.DoesNotExist:
        return Response({
            'status'  : 'invalid',
            'message' : '❌ Invalid ticket — not found in system.'
        }, status=status.HTTP_404_NOT_FOUND)

    # ── Already scanned ──────────────────────────────────────
    if ticket.status == 'scanned':
        ScanLog.objects.create(
            ticket     = ticket,
            scanned_by = request.user,
            was_valid  = False,
            notes      = 'Ticket already used.'
        )
        return Response({
            'status'  : 'already_used',
            'message' : '⚠️ Ticket already scanned!',
            'scanned_at' : ticket.scanned_at,
        }, status=status.HTTP_400_BAD_REQUEST)

    # ── Payment not completed ────────────────────────────────
    if not ticket.is_valid:
        return Response({
            'status'  : 'payment_pending',
            'message' : '❌ Payment not completed for this ticket.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # ── Valid — mark as scanned ──────────────────────────────
    ticket.status     = 'scanned'
    ticket.scanned_at = timezone.now()
    ticket.scanned_by = request.user
    ticket.save()

    ScanLog.objects.create(
        ticket     = ticket,
        scanned_by = request.user,
        was_valid  = True,
        notes      = 'Entry granted.'
    )

    return Response({
        'status'   : 'valid',
        'message'  : '✅ Ticket verified! Entry granted.',
        'attendee' : ticket.user.username,
        'event'    : ticket.event.title,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_tickets_view(request, event_id):
    """
    Get all tickets for an event. Host only.
    GET /api/tickets/event/<event_id>/
    """
    if request.user.role != 'host':
        return Response({
            'message': 'Only Hosts can view event tickets.'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        event = Event.objects.get(pk=event_id, host=request.user)
    except Event.DoesNotExist:
        return Response({
            'message': 'Event not found or not yours.'
        }, status=status.HTTP_404_NOT_FOUND)

    tickets    = Ticket.objects.filter(event=event)
    serializer = TicketSerializer(tickets, many=True)

    return Response({
        'event'         : event.title,
        'total_tickets' : tickets.count(),
        'scanned'       : tickets.filter(status='scanned').count(),
        'remaining'     : tickets.filter(status='active').count(),
        'tickets'       : serializer.data,
    }, status=status.HTTP_200_OK)


# ── Add these imports at the top of views.py ─────────────────────
from django.conf import settings
from .razorpay_utils import create_razorpay_order, verify_razorpay_payment


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_order_view(request):
    """
    Step 1 of payment — Create a Razorpay order.
    Frontend uses this order_id to open Razorpay checkout.
    POST /api/tickets/payment/create-order/
    """
    event_id = request.data.get('event_id')

    # ── Validate event ───────────────────────────────────────
    try:
        event = Event.objects.get(pk=event_id, is_active=True)
    except Event.DoesNotExist:
        return Response({
            'message': 'Event not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    # ── Check already purchased ──────────────────────────────
    if Ticket.objects.filter(event=event, user=request.user).exists():
        return Response({
            'message': 'You already have a ticket for this event!'
        }, status=status.HTTP_400_BAD_REQUEST)

    # ── Check availability ───────────────────────────────────
    if event.is_sold_out:
        return Response({
            'message': 'Sorry! This event is sold out.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # ── Create Razorpay order ────────────────────────────────
    try:
        order = create_razorpay_order(
            amount   = float(event.ticket_price),
            currency = 'INR',
            notes    = {
                'event_id'   : str(event.id),
                'event_name' : event.title,
                'user_id'    : str(request.user.id),
                'username'   : request.user.username,
            }
        )
    except Exception as e:
        return Response({
            'message': f'Payment order creation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ── Create pending ticket ────────────────────────────────
    ticket = Ticket.objects.create(
        event              = event,
        user               = request.user,
        payment_status     = 'pending',
        amount_paid        = event.ticket_price,
        razorpay_order_id  = order['id'],
    )

    return Response({
        'message'         : 'Payment order created. Complete payment to confirm ticket.',
        'order_id'        : order['id'],
        'amount'          : float(event.ticket_price),
        'currency'        : 'INR',
        'ticket_id'       : ticket.id,
        'razorpay_key_id' : settings.RAZORPAY_KEY_ID,
        'event_title'     : event.title,
        'username'        : request.user.username,
        'email'           : request.user.email,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment_view(request):
    """
    Step 2 of payment — Verify Razorpay payment signature.
    On success — ticket is confirmed and QR code is generated.
    POST /api/tickets/payment/verify/
    """
    razorpay_order_id   = request.data.get('razorpay_order_id')
    razorpay_payment_id = request.data.get('razorpay_payment_id')
    razorpay_signature  = request.data.get('razorpay_signature')

    # ── Validate inputs ──────────────────────────────────────
    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return Response({
            'message': 'All payment fields are required.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # ── Find ticket ──────────────────────────────────────────
    try:
        ticket = Ticket.objects.get(
            razorpay_order_id = razorpay_order_id,
            user              = request.user
        )
    except Ticket.DoesNotExist:
        return Response({
            'message': 'Ticket not found for this order.'
        }, status=status.HTTP_404_NOT_FOUND)

    # ── Verify signature ─────────────────────────────────────
    is_valid = verify_razorpay_payment(
        razorpay_order_id,
        razorpay_payment_id,
        razorpay_signature
    )

    if is_valid:
        # ── Payment successful ───────────────────────────────
        ticket.payment_status      = 'completed'
        ticket.razorpay_payment_id = razorpay_payment_id
        ticket.qr_code             = generate_qr_code(ticket.ticket_code, ticket.id)
        ticket.save()

        return Response({
            'message' : '🎉 Payment successful! Your ticket is confirmed.',
            'ticket'  : TicketSerializer(ticket).data,
        }, status=status.HTTP_200_OK)

    else:
        # ── Payment failed ───────────────────────────────────
        ticket.payment_status = 'failed'
        ticket.save()

        return Response({
            'message': '❌ Payment verification failed. Please try again.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status_view(request, ticket_id):
    """
    Check payment status of a ticket.
    GET /api/tickets/payment/status/<ticket_id>/
    """
    try:
        ticket = Ticket.objects.get(pk=ticket_id, user=request.user)
    except Ticket.DoesNotExist:
        return Response({
            'message': 'Ticket not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'ticket_id'        : ticket.id,
        'event'            : ticket.event.title,
        'amount_paid'      : float(ticket.amount_paid),
        'payment_status'   : ticket.payment_status,
        'razorpay_order_id': ticket.razorpay_order_id,
        'ticket_confirmed' : ticket.payment_status in ['completed', 'free'],
    }, status=status.HTTP_200_OK)