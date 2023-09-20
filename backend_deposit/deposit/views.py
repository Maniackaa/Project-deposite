
import logging
import time
import uuid

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import urlencode

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request



from deposit.forms import DepositForm, DepositImageForm
from deposit.func import img_path_to_str
from deposit.models import BadScreen, Incoming, Deposit
from deposit.screen_response import screen_text_to_pay
from deposit.serializers import IncomingSerializer

logger = logging.getLogger(__name__)
# logging.config.dictConfig(LOGCONFIG)


def index(request, *args, **kwargs):
    logger.debug(f'index {request}')
    form = DepositForm(request.POST or None,
                       files=request.FILES or None, initial={'phone': '+994', 'uid': uuid.uuid4()})
    if request.method == 'POST':
        logger.debug('index POST')
        if form.is_valid():
            form.save(commit=False)
            return redirect('deposit:deposit_confirm',
                            form=form,
                            )
        else:
            logger.debug('form.invalid')
            raise ValueError()
    template = 'deposit/index.html'
    context = {'hello': f'Привет!\n', 'form': form}
    return render(request, template, context)


def deposit_confirm(request):
    try:
        logger.debug(f'deposit_confirm {request}')
        form = DepositForm(request.POST or request.GET or None, files=request.FILES or None)
        template = 'deposit/deposit_confirm.html'
        if request.method == 'POST':
            if form.is_valid():
                template = 'deposit/deposit_confirm.html'
                context = {'form': form}
                return render(request, template_name=template, context=context)

        logger.debug(f'GET ')
        context = {'form': form}
        return render(request, template_name=template, context=context)
    except Exception as err:
        logger.error('ошибка')
        raise err


def deposit_created(request):
    logger.debug(f'deposit_created: {request}')
    if request.method == 'GET':
        logger.debug(f'deposit_created {request}')
        form = DepositImageForm(request.GET, files=request.FILES or None)
        uid = form.get_context()['hidden_fields'][0].value()
        if form.is_valid():
            form.save()
        else:
            pass
        template = 'deposit/deposit_created.html'
        context = {'uid': uid, 'form': form}
        return render(request, template_name=template, context=context)
    if request.method == 'POST':
        screen = request._files.get('pay_screen')
        form = DepositImageForm(request.POST, files=request.FILES or None, initial={'pay_screen': screen})
        uid = form.get_context()['hidden_fields'][0].value()
        template = 'deposit/deposit_created.html'
        screen = form.files.get('pay_screen')
        if screen:
            print(screen, screen.__dict__)
            deposit = Deposit.objects.get(uid=uid)
            deposit.pay_screen = screen
            deposit.save()
            print(form)
        context = {'uid': uid, 'form': form, 'deposit': deposit, 'pay_screen': screen}
        return render(request, template_name=template, context=context)


def deposit_status(request, uid):
    logger.debug(f'deposit_status {request}')
    template = 'deposit/deposit_status.html'
    deposite = Deposit.objects.filter(uid=uid).first()
    context = {'deposit': deposite}
    return render(request, template_name=template, context=context)



@api_view(['POST'])
def screen(request: Request):
    """
    Прием сриншота
    """
    try:
        # params_example {'name': '/DCIM/Screen.jpg', 'worker': 'Station 1}
        logger.debug(f'{request.data} {request._request.get_host()}')

        image = request.data.get('image')
        worker = request.data.get('worker')
        name = request.data.get('name')

        if not image or not image.file:
            logger.info(f'Запрос без изображения')
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST,
                                reason='no screen',
                                charset='utf-8')

        file_bytes = image.file.read()
        text = img_path_to_str(file_bytes)
        logger.debug(f'Распознан текст: {text}')
        pay = screen_text_to_pay(text)
        logger.debug(f'Распознан pay: {pay}')

        pay_status = pay.pop('status')
        errors = pay.pop('errors')
        sms_type = pay.get('type')

        # Если шаблон найден:
        if sms_type:
            transaction = pay.get('transaction')

            is_incoming_duplicate = Incoming.objects.filter(transaction=transaction)
            # Если дубликат:
            if is_incoming_duplicate:
                return HttpResponse(status=status.HTTP_200_OK,
                                    reason='Incoming duplicate',
                                    charset='utf-8')
            # Если статус отличается от успешно
            if pay_status.lower() != 'успешно':
                logger.debug(f'fПлохой статус: {pay}.')
                # Проверяем на дубликат в BadScreen
                is_duplicate = BadScreen.objects.filter(transaction=transaction).exists()
                if not is_duplicate:
                    logger.debug('Сохраняем в BadScreen')
                    BadScreen.objects.create(name=name, worker=worker, image=image,
                                             transaction=transaction, type=sms_type)
                    return HttpResponse(status=status.HTTP_200_OK,
                                        reason='New BadScreen',
                                        charset='utf-8')
                else:
                    logger.debug('Дубликат в BadScreen')
                    return HttpResponse(status=status.HTTP_200_OK,
                                        reason='duplicate in BadScreen',
                                        charset='utf-8')

            # Действия со статусом Успешно
            serializer = IncomingSerializer(data=pay)
            if serializer.is_valid():
                # Сохраянем Incoming
                logger.debug(f'Incoming serializer valid. Сохраняем транзакцию {transaction}')
                serializer.save(worker=worker, image=image)
                return HttpResponse(status=status.HTTP_201_CREATED,
                                    reason='created',
                                    charset='utf-8')
            else:
                # Если не сохранилось в Incoming
                logger.debug('Incoming serializer invalid')
                logger.debug(f'serializer errors: {serializer.errors}')
                transaction_error = serializer.errors.get('transaction')

                # Если просто дубликат:
                if transaction_error:
                    transaction_error_code = transaction_error[0].code
                    if transaction_error_code == 'unique':
                        # Такая транзакция уже есть. Дупликат.
                        return HttpResponse(status=status.HTTP_201_CREATED,
                                            reason='Incoming duplicate',
                                            charset='utf-8')

                # Обработа неизвестных ошибок при сохранении
                logger.warning('Неизестная ошибка')
                if not BadScreen.objects.filter(transaction=transaction).exists():
                    BadScreen.objects.create(name=name, worker=worker, image=image,
                                             transaction=transaction, type=sms_type)
                    return HttpResponse(status=status.HTTP_200_OK,
                                        reason='invalid serializer. Add to trash',
                                        charset='utf-8')
                return HttpResponse(status=status.HTTP_200_OK,
                                    reason='invalid serializer. Duplicate in trash',
                                    charset='utf-8')

        else:
            # Действие если скрин не по известному шаблону
            BadScreen.objects.create(name=name, worker=worker, image=image)
            return HttpResponse(status=status.HTTP_200_OK,
                                reason='not recognize',
                                charset='utf-8')

    # Ошибка при обработке
    except Exception as err:
        logger.error(err, exc_info=True)
        logger.debug(f'{request.data} {request._request.get_host()}')
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST,
                            reason=f'{err}',
                            charset='utf-8')
