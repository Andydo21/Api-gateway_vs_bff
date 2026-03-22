from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from .serializers import NotificationSerializer

@api_view(['POST'])
def send_notification(request):
    """
    Internal API to send a notification to a user.
    Expected data: { "user_id": 1, "message": "hello", "notification_type": "info" }
    """
    user_id = request.data.get('user_id')
    message = request.data.get('message')
    notification_type = request.data.get('notification_type', 'info')

    if not user_id or not message:
        return Response({'error': 'user_id and message are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Save to database
    Notification.objects.create(
        user_id=user_id,
        message=message,
        notification_type=notification_type
    )

    # Send to WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user_id}',
        {
            'type': 'send_notification',
            'message': message,
            'notification_type': notification_type
        }
    )


@api_view(['GET'])
def list_notifications(request):
    """
    Get all notifications for a specific user ID.
    Query Params: ?user_id=1
    """
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    notifs = Notification.objects.filter(user_id=user_id).order_by('-created_at')[:50]
    serializer = NotificationSerializer(notifs, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    })

@api_view(['PUT'])
def mark_as_read(request, pk):
    """
    Mark a notification as read.
    """
    try:
        notif = Notification.objects.get(pk=pk)
        notif.is_read = True
        notif.save()
        return Response({'success': True})
    except Notification.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
