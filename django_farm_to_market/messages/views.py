from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Message
from .serializers import MessageSerializer
from django.db import models

class IsParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user or obj.receiver == request.user

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_read']

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            models.Q(sender=user) | models.Q(receiver=user)
        )

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        if message.receiver == request.user:
            message.is_read = True
            message.save()
            return Response({'status': 'marked as read'})
        return Response(
            {'error': 'Only the receiver can mark messages as read'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = Message.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count}) 