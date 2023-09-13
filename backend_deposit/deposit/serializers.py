from rest_framework import serializers

from .models import Incoming



class IncomingSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Incoming

    def create(self, validated_data):
        incoming = Incoming.objects.create(**validated_data)
        return incoming
