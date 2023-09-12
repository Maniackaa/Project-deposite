import logging

from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import mixins, status, viewsets

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from api.serializers import ScreenSerializer
from backend_deposit.settings import BASE_DIR, LOGCONFIG

from deposit.models import Screen

User = get_user_model()

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGCONFIG)


class ScreenViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    logger.debug('ScreenViewSet')
    queryset = Screen.objects.all()
    serializer_class = ScreenSerializer
    pagination_class = LimitOffsetPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        logger.debug('')
        if serializer.is_valid(raise_exception=False):
            logger.debug('')
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
