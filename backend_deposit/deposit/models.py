import datetime
import logging
import re

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.db.transaction import atomic
from django.dispatch import receiver

from django.db.models.signals import post_delete, post_save

from backend_deposit.settings import TZ

logger = logging.getLogger(__name__)


class Incoming(models.Model):
    register_date = models.DateTimeField('Время добавления в базу', auto_now=True)
    response_date = models.DateTimeField('Распознанное время', null=True, blank=True)
    recipient = models.CharField('Получатель', max_length=50, null=True, blank=True)
    sender = models.CharField('Отравитель/карта', max_length=50, null=True, blank=True)
    pay = models.FloatField('Платеж')
    balance = models.FloatField('Баланс', null=True, blank=True)
    transaction = models.IntegerField('Транзакция', null=True, unique=True, blank=True)
    type = models.CharField(max_length=20, default='unknown')
    worker = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to='screens/',
                              verbose_name='скрин', null=True, blank=True)
    confirmed_deposit = models.OneToOneField('Deposit', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        string = f'Incoming {self.id} {self.transaction}, pay: {self.pay}'
        return string


class Deposit(models.Model):
    uid = models.CharField(max_length=36, db_index=True, unique=True, null=True, blank=True)
    register_time = models.DateTimeField('Время добавления в базу', auto_now_add=True)
    change_time = models.DateTimeField('Время изменения в базе', auto_now=True)
    phone = models.CharField('Телефон отправителя')
    pay_sum = models.IntegerField('Сумма платежа', validators=[MinValueValidator(5)])
    input_transaction = models.IntegerField('Номер транзакции из чека',
                                            null=True, blank=True, help_text='Номер транзакции из чека',
                                            validators=[MinValueValidator(50000000), MaxValueValidator(99999999)])
    status = models.CharField('Статус депозита', default='pending')
    pay_screen = models.ImageField(upload_to='pay_screens/',
                                   verbose_name='Чек об оплате', null=True, blank=True, help_text='Скриншот чека')
    confirmed_incoming = models.OneToOneField(Incoming, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        string = f'Deposit {self.id}. {self.input_transaction}, pay: {self.pay_sum}, pay_screen: {self.pay_screen}'
        return string


class BadScreen(models.Model):
    name = models.CharField(unique=False, max_length=200)
    image = models.ImageField(upload_to='bad_screens/',
                              verbose_name='скрин')
    incoming_time = models.DateTimeField('Время добавления в базу', auto_now=True)
    worker = models.CharField(max_length=50, null=True)
    transaction = models.IntegerField('Транзакция', null=True, unique=True, blank=True)
    type = models.CharField(max_length=20, default='unknown')


@receiver(post_delete, sender=BadScreen)
def bad_screen_image_delete(sender, instance, **kwargs):
    if instance.image.name:
        instance.image.delete(False)


@receiver(post_delete, sender=Incoming)
def screen_image_delete(sender, instance, **kwargs):
    if instance.image.name:
        instance.image.delete(False)


@receiver(post_save, sender=Incoming)
def after_save_incoming(sender, instance: Incoming, **kwargs):
    try:
        if instance.confirmed_deposit:
            logger.debug('incoming post_save return')
            return
        logger.debug(f'Действие после сохранения корректного скрина: {instance}')
        pay = instance.pay
        transaction = instance.transaction
        transaction_list = [transaction - 1, transaction + 1, transaction + 2]
        treshold = datetime.datetime.now(tz=TZ) - datetime.timedelta(minutes=10)
        logger.debug(f'Ищем депозиты не позднее чем: {str(treshold)}')
        deposits = Deposit.objects.filter(
            status='pending',
            pay_sum=pay,
            register_time__gte=treshold,
            input_transaction__in=transaction_list
        ).all()
        logger.debug(f'Найденные deposits: {deposits}')
        if deposits:
            deposit = deposits.first()
            logger.debug(f'Подтверждаем депозит {deposit}')
            deposit.confirmed_incoming = instance
            deposit.status = 'confirmed'
            deposit.save()
            logger.debug(f'Депозит подтвержден: {deposit}')
            logger.debug(f'Сохраняем confirmed_deposit: {deposit}')
            instance.confirmed_deposit = deposit
            instance.save()

    except Exception as err:
        logger.error(err, exc_info=True)


@transaction.atomic
@receiver(post_save, sender=Deposit)
def after_save_deposit(sender, instance: Deposit, **kwargs):
    try:
        logger.debug(f'Действие после сохранения депозита: {instance}')
        logger.debug(f'sender: {sender}')
        if instance.input_transaction and instance.status == 'pending':
            treshold = datetime.datetime.now(tz=TZ) - datetime.timedelta(minutes=10)
            logger.debug(f'Ищем скрины не позднее чем: {str(treshold)}')
            logger.debug(f'input_transaction: {instance.input_transaction}, {type(instance.input_transaction)}')
            transaction_list = [instance.input_transaction - 1,
                                instance.input_transaction + 1,
                                instance.input_transaction + 2]
            logger.debug(f'transaction_list: {transaction_list}')
            incomings = Incoming.objects.filter(
                register_date__gte=treshold,
                pay=instance.pay_sum,
                transaction__in=transaction_list,
                confirmed_deposit=None
            ).order_by('-id').all()
            logger.debug(f'Найденные скрины: {incomings}')
            if incomings:
                incoming = incomings.first()
                incoming.confirmed_deposit = instance
                instance.status = 'approved'
                incoming.save()
                instance.save()
        else:
            logger.debug('deposit post_save return')

    except Exception as err:
        logger.error(err, exc_info=True)
