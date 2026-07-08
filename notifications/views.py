from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer, NotificationListSerializer
from citizens.models import Citizen


def _get_citizen_or_error(user):
    try:
        return Citizen.objects.get(user=user)
    except Citizen.DoesNotExist:
        return None


@api_view(['GET'])
def list_notifications(request):
    citizen = _get_citizen_or_error(request.user)
    if not citizen:
        return Response(
            {"detail": "Solo ciudadanos pueden ver notificaciones"},
            status=status.HTTP_403_FORBIDDEN,
        )

    unread_only = request.query_params.get('unread_only', '').lower() == 'true'

    qs = Notification.objects.filter(citizen=citizen)
    if unread_only:
        qs = qs.filter(is_read=False)
    qs = qs.order_by('-sent_at')

    notifications = qs.select_related('record').all()
    total = Notification.objects.filter(citizen=citizen).count()
    unread = Notification.objects.filter(citizen=citizen, is_read=False).count()

    serializer = NotificationListSerializer({
        'total': total,
        'unread': unread,
        'notifications': notifications,
    })
    return Response(serializer.data)


@api_view(['GET'])
def list_unread(request):
    citizen = _get_citizen_or_error(request.user)
    if not citizen:
        return Response(
            {"detail": "Solo ciudadanos pueden ver notificaciones"},
            status=status.HTTP_403_FORBIDDEN,
        )

    qs = Notification.objects.filter(citizen=citizen, is_read=False).order_by('-sent_at')
    notifications = qs.select_related('record').all()
    total = Notification.objects.filter(citizen=citizen).count()
    unread = len(notifications)

    serializer = NotificationListSerializer({
        'total': total,
        'unread': unread,
        'notifications': notifications,
    })
    return Response(serializer.data)


@api_view(['PUT'])
def mark_as_read(request, pk):
    citizen = _get_citizen_or_error(request.user)
    if not citizen:
        return Response(
            {"detail": "Solo ciudadanos pueden marcar notificaciones"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        notification = Notification.objects.get(id=pk, citizen=citizen)
    except Notification.DoesNotExist:
        return Response(
            {"detail": "Notificación no encontrada"},
            status=status.HTTP_404_NOT_FOUND,
        )

    notification.is_read = True
    notification.save()

    serializer = NotificationSerializer(notification)
    return Response(serializer.data)


@api_view(['POST'])
def mark_all_read(request):
    citizen = _get_citizen_or_error(request.user)
    if not citizen:
        return Response(
            {"detail": "Solo ciudadanos pueden marcar notificaciones"},
            status=status.HTTP_403_FORBIDDEN,
        )

    count = Notification.objects.filter(citizen=citizen, is_read=False).update(is_read=True)

    return Response({
        "mensaje": f"{count} notificaciones marcadas como leídas",
        "cantidad": count,
    })
