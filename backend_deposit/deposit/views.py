
import logging
import time
import uuid

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.views.generic import ListView, DetailView

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request


from deposit.forms import DepositForm, DepositImageForm, DepositTransactionForm
from deposit.func import img_path_to_str
from deposit.models import BadScreen, Incoming, Deposit
from deposit.screen_response import screen_text_to_pay
from deposit.serializers import IncomingSerializer

logger = logging.getLogger(__name__)


def index(request, *args, **kwargs):
    try:
        logger.debug(f'index {request}')
        uid = uuid.uuid4()
        form = DepositForm(request.POST or None, files=request.FILES or None, initial={'phone': '+994', 'uid': uid})
        if request.method == 'POST':
            logger.debug('index POST')
            data = request.POST
            uid = data.get('uid')
            deposit = Deposit.objects.filter(uid=uid).first()
            if deposit:
                template = 'deposit/deposit_created.html'
                form = DepositTransactionForm(request.POST, instance=deposit)
                context = {'form': form, 'deposit': deposit}
                return render(request, template_name=template, context=context)
            if form.is_valid():
                logger.debug('form valid')
                form.save()
                uid = form.cleaned_data.get('uid')
                deposit = Deposit.objects.get(uid=uid)
                logger.debug(f'form save')
                template = 'deposit/deposit_created.html'
                form = DepositTransactionForm(request.POST, instance=deposit)
                context = {'form': form, 'deposit': deposit}
                return render(request, template_name=template, context=context)
            else:
                template = 'deposit/index.html'
                context = {'form': form}
                return render(request, template_name=template, context=context)

        logger.debug(f'index GET ')

        context = {'form': form}
        template = 'deposit/index.html'
        return render(request, template_name=template, context=context)
    except Exception as err:
        logger.error('ошибка', exc_info=True)
        raise err


def deposit_created(request):
    logger.debug(f'deposit_created: {request}')
    if request.method == 'POST':
        data = request.POST
        print('POST deposit_created', data)
        uid = data['uid']
        phone = data['phone']
        pay = data['pay_sum']
        deposit = Deposit.objects.filter(uid=uid).exists()
        print(deposit)
        print(uid, phone, pay)
        if not deposit:
            form = DepositTransactionForm(request.POST or None, files=request.FILES or None, initial={'phone': phone, 'uid': uid, 'pay_sum': pay})
            if form.is_valid():
                form.save()
                logger.debug('Форма сохранена')
            else:
                logger.debug(f'Форма не валидная: {form}')
                for error in form.errors:
                    logger.warning(f'{error}')
                template = 'deposit/index.html'
                context = {'form': form}
                return render(request, template_name=template, context=context)

        deposit = Deposit.objects.get(uid=uid)
        logger.debug(f'deposit: {deposit}')
        input_transaction = data.get('input_transaction') or None
        logger.debug(f'input_transaction: {input_transaction}')
        deposit.input_transaction = input_transaction
        form = DepositTransactionForm(request.POST, files=request.FILES, instance=deposit)
        if form.is_valid():
            form.save()
        template = 'deposit/deposit_created.html'

        context = {'form': form, 'deposit': deposit, 'pay_screen': None}
        return render(request, template_name=template, context=context)


def deposit_status(request, uid):
    logger.debug(f'deposit_status {request}')
    template = 'deposit/deposit_status.html'
    deposit = get_object_or_404(Deposit, uid=uid)
    form = DepositImageForm(request.POST, files=request.FILES, instance=deposit)
    if request.method == 'POST' and form.has_changed():
        logger.debug(f'has_changed: {form.has_changed()}')
        if form.is_valid():
            form.save()
        else:
            form = DepositTransactionForm(instance=deposit, files=request.FILES)
            template = 'deposit/deposit_created.html'
            context = {'form': form, 'deposit': deposit, 'pay_screen': deposit.pay_screen}
            return render(request, template_name=template, context=context)
        form = DepositImageForm(instance=deposit)
        context = {'deposit': deposit, 'form': form}
        return render(request, template_name=template, context=context)
    # form = DepositImageForm(initial=deposit.__dict__, instance=deposit)
    context = {'deposit': deposit, 'form': form}
    logger.debug(f'has_changed: {form.has_changed()}')

    return render(request, template_name=template, context=context)


# class DepositList(ListView):
#     model = Deposit
#     paginate_by = 10
#     context_object_name = 'posts'
#     template_name = 'deposit/deposit_list.html'
#
#     # @method_decorator(login_required)
#     # def dispatch(self, request, *args, **kwargs):
#     #     return super(DepositList, self).dispatch(request, *args, **kwargs)
#
#     def get_queryset(self):
#         return Deposit.objects.filter()


def make_page_obj(request, posts, numbers_of_posts=10):
    paginator = Paginator(posts, numbers_of_posts)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def deposits_list(request):
    template = 'deposit/deposit_list.html'
    deposits = Deposit.objects.order_by('-id').all()
    context = {'page_obj': make_page_obj(request, deposits)}
    return render(request, template, context)


def deposits_list_pending(request):
    template = 'deposit/deposit_list.html'
    deposits = Deposit.objects.order_by('-id').filter(status='pending').all()
    context = {'page_obj': make_page_obj(request, deposits)}
    return render(request, template, context)


class ShowDeposit(DetailView):
    model = Deposit
    template_name = 'deposit/deposit.html'














@api_view(['POST'])
def screen(request: Request):
    """
    Прием сриншота
    """
    try:
        host = request.META["HTTP_HOST"]  # получаем адрес сервера
        user_agent = request.META.get("HTTP_USER_AGENT")  # получаем данные бразера
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        path = request.path
        logger.debug(f'request.data: {request.data},'
                     f' host: {host},'
                     f' user_agent: {user_agent},'
                     f' path: {path},'
                     f' forwarded: {forwarded}')

        # params_example {'name': '/DCIM/Screen.jpg', 'worker': 'Station 1}
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
        if errors:
            logger.warning(f'errors: {errors}')
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
            try:
                # Действие если скрин не по известному шаблону
                logger.debug('скрин не по известному шаблону')
                BadScreen.objects.create(name=name, worker=worker, image=image)
                logger.debug(f'BadScreen сохранен')
                logger.debug(f'Возвращаем статус 200: not recognize')
                return HttpResponse(status=status.HTTP_200_OK,
                                    reason='not recognize',
                                    charset='utf-8')
            except Exception as err:
                logger.error(err, exc_info=True)

    # Ошибка при обработке
    except Exception as err:
        logger.debug(f'Ошибка при обработке скрина: {err}')
        logger.error(err, exc_info=True)
        logger.debug(f'{request.data}')
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST,
                            reason=f'{err}',
                            charset='utf-8')
