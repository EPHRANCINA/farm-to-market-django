from rest_framework import serializers
from .models import Message
from auth_app.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='receiver'
    )

    class Meta:
        model = Message
        fields = ('id', 'sender', 'receiver', 'receiver_id', 'content', 
                 'is_read', 'created_at')
        read_only_fields = ('id', 'sender', 'is_read', 'created_at')

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data) 