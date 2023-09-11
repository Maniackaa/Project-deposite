import base64

import rest_framework.pagination
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from deposit.models import Screen

User = get_user_model()




class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class ScreenSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Screen
        fields = (
            "id",
            "name",
            "image",
        )

    def create(self, validated_data, *args, **kwargs):
        screen = Screen.objects.create(**validated_data)
        return screen

    def validate(self, attrs):
        request = self.context.get('request')
        return attrs
