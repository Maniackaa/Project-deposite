
import logging
import time

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import urlencode

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request


from backend_deposit.settings import LOGCONFIG
from deposit.forms import DepositForm
from deposit.func import img_path_to_str
from deposit.models import BadScreen, Incoming
from deposit.screen_response import screen_text_to_pay
from deposit.serializers import IncomingSerializer

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGCONFIG)


def index(request, *args, **kwargs):
    form = DepositForm(request.POST or None, files=request.FILES or None, initial={'phone': '+994'})
    if form.is_valid():
        form.save(commit=False)
        return redirect('deposit:deposit_confirm',
                        phone=form.data.get('phone'),
                        pay=form.data.get('pay_sum'))
    template = 'deposit/index.html'
    context = {'hello': f'Привет!\n', 'form': form}
    return render(request, template, context)


def deposit_confirm(request, phone=None, pay=None):
    print(phone, pay)
    template = 'deposit/deposit_confirm.html'
    context = {'hello': f'Подтвердите ваши данные:', 'phone': phone, 'pay': pay}
    return render(request, template, context)


@api_view(['POST'])
def screen(request: Request):
    logger.debug(f'Запрос: {request}')
    logger.debug(f'{request.data}')
    # logger.debug(f'data:, {str(request.__dict__)}')
    logger.info(request._request.headers)
    logger.info(request._request.get_host())
    image = request.data.get('image')
    if image:
        file_bytes = image.file.read()
        logger.debug(f'file_bytes: {file_bytes[:10]}')
        if file_bytes:
            text = img_path_to_str(file_bytes)
            pay = screen_text_to_pay(text)
            worker = request.data.get('WORKER')
            name = request.data.get('name')
            pay_status = pay.pop('status')
            errors = pay.pop('errors')
            sms_type = pay.get('type')
            transaction = pay.get('transaction')
            if pay_status.lower() != 'успешно' and sms_type != '':
                logger.debug('trash')
                is_duplicate = BadScreen.objects.filter(transaction=transaction).exists()
                if not is_duplicate:
                    logger.debug('Мусор не дубликат')
                    BadScreen.objects.create(name=name, worker=worker, image=image, transaction=transaction, type=sms_type)
                    return HttpResponse(status=status.HTTP_200_OK,
                                        reason='BadScreen',
                                        charset='utf-8')
                else:
                    logger.debug('Дубликат - уже есть в BadScreen')
                    return HttpResponse(status=status.HTTP_200_OK,
                                        reason='duplicate in BadScreen',
                                        charset='utf-8')

            serializer = IncomingSerializer(data=pay)
            if serializer.is_valid():
                logger.debug('valid')
                serializer.save(worker=worker, image=image)
                return HttpResponse(status=status.HTTP_201_CREATED,
                                    reason='created',
                                    charset='utf-8')
            else:
                logger.debug('invalid')
                logger.debug(serializer.errors)
                is_duplicate_incoming = BadScreen.objects.filter(transaction=transaction).exists()
                is_duplicate_trash = Incoming.objects.filter(transaction=transaction).exists()
                if is_duplicate_trash or is_duplicate_incoming:
                    return HttpResponse(status=status.HTTP_200_OK,
                                        reason='duplicate',
                                        charset='utf-8')
                else:
                    BadScreen.objects.create(name=name, worker=worker, image=image, transaction=transaction, type=sms_type)
                    return HttpResponse(status=status.HTTP_200_OK,
                                        reason='trash',
                                        charset='utf-8')
    return HttpResponse(status=status.HTTP_400_BAD_REQUEST,
                        reason='bad request',
                        charset='utf-8')
