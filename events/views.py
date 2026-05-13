from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Event
from .serializers import EventSerializer, EventCreateSerializer
from .permissions import IsHostOrReadOnly, IsEventOwner


@api_view(['GET'])
@permission_classes([AllowAny])
def event_list_view(request):
    """
    List all active events.
    Supports filtering by event_type and city.
    GET /api/events/
    """
    events = Event.objects.filter(is_active=True)

    # ── Optional filters ─────────────────────────────────────
    event_type = request.query_params.get('type')
    city       = request.query_params.get('city')
    search     = request.query_params.get('search')

    if event_type:
        events = events.filter(event_type=event_type)
    if city:
        events = events.filter(city__icontains=city)
    if search:
        events = events.filter(title__icontains=search)

    serializer = EventSerializer(events, many=True)
    return Response({
        'count'  : events.count(),
        'events' : serializer.data,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def event_detail_view(request, pk):
    """
    Get a single event by ID.
    GET /api/events/<id>/
    """
    try:
        event = Event.objects.get(pk=pk, is_active=True)
    except Event.DoesNotExist:
        return Response({
            'message': 'Event not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = EventSerializer(event)
    return Response({
        'event': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def event_create_view(request):
    """
    Create a new event. Hosts only.
    POST /api/events/create/
    """
    if request.user.role != 'host':
        return Response({
            'message': 'Only Hosts can create events.'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = EventCreateSerializer(data=request.data)

    if serializer.is_valid():
        event = serializer.save(host=request.user)
        return Response({
            'message': f'Event "{event.title}" created successfully!',
            'event'  : EventSerializer(event).data,
        }, status=status.HTTP_201_CREATED)

    return Response({
        'message': 'Event creation failed.',
        'errors' : serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def event_update_view(request, pk):
    """
    Update an event. Only the host owner can update.
    PUT/PATCH /api/events/<id>/update/
    """
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({
            'message': 'Event not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    # Only the event owner can update
    if event.host != request.user:
        return Response({
            'message': 'You can only update your own events.'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = EventCreateSerializer(
        event,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        event = serializer.save()
        return Response({
            'message': f'Event "{event.title}" updated successfully!',
            'event'  : EventSerializer(event).data,
        }, status=status.HTTP_200_OK)

    return Response({
        'message': 'Update failed.',
        'errors' : serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def event_delete_view(request, pk):
    """
    Delete an event. Only the host owner can delete.
    DELETE /api/events/<id>/delete/
    """
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({
            'message': 'Event not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    if event.host != request.user:
        return Response({
            'message': 'You can only delete your own events.'
        }, status=status.HTTP_403_FORBIDDEN)

    event_title = event.title
    event.delete()

    return Response({
        'message': f'Event "{event_title}" deleted successfully!'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def host_events_view(request):
    """
    Get all events created by the logged-in host.
    GET /api/events/my-events/
    """
    if request.user.role != 'host':
        return Response({
            'message': 'Only Hosts can access this.'
        }, status=status.HTTP_403_FORBIDDEN)

    events     = Event.objects.filter(host=request.user)
    serializer = EventSerializer(events, many=True)

    return Response({
        'count'  : events.count(),
        'events' : serializer.data,
    }, status=status.HTTP_200_OK)