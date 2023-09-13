import json
import logging
import re
from io import BytesIO

import cv2
import numpy as np
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from backend_deposit.settings import LOGCONFIG
from deposit.func import img_path_to_str, response_m10, response_m10_short
from deposit.models import BadScreen, Incoming
from deposit.screen_response import screen_text_to_pay
from deposit.serializers import IncomingSerializer

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGCONFIG)


def index(request):
    template = 'deposit/index.html'
    context = {'hello': 'Привет'}
    return render(request, template, context)


@api_view(['POST'])
def screen(request: Request):
    image = request.data.get('image')
    file_bytes = image.file.read()
    text = img_path_to_str(file_bytes)
    pay = screen_text_to_pay(text)
    worker = request.data.get('WORKER')
    name = request.data.get('name')
    pay_status = pay.pop('status')
    errors = pay.pop('errors')
    sms_type = pay.get('type')
    transaction = pay.get('transaction')
    if pay_status.lower() != 'успешно' and sms_type != '':
        print('trash')
        is_duplicate = BadScreen.objects.filter(transaction=transaction).exists()
        if not is_duplicate:
            BadScreen.objects.create(name=name, worker=worker, image=image, transaction=transaction, type=sms_type)
            return HttpResponse(status=status.HTTP_200_OK,
                                reason='BadScreen',
                                charset='utf-8')
        else:
            print('Дубликат в BadScreen')
            return HttpResponse(status=status.HTTP_200_OK,
                                reason='duplicate in BadScreen',
                                charset='utf-8')


    serializer = IncomingSerializer(data=pay)
    if serializer.is_valid():
        print('valid')
        serializer.save(worker=worker, image=image)
        return HttpResponse(status=status.HTTP_201_CREATED,
                            reason='created',
                            charset='utf-8')
    else:
        print('invalid')
        print(serializer.errors)
        is_duplicate = BadScreen.objects.filter(transaction=transaction).exists()
        if not is_duplicate:
            BadScreen.objects.create(name=name, worker=worker, image=image, transaction=transaction, type=sms_type)
            return HttpResponse(status=status.HTTP_200_OK,
                                reason='trash',
                                charset='utf-8')
        else:
            return HttpResponse(status=status.HTTP_200_OK,
                                reason='trash_duplicate',
                                charset='utf-8')
