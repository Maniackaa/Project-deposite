from django.core.validators import MinValueValidator
from django.db import models
from django.dispatch import receiver

from django.db.models.signals import post_delete


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


class BadScreen(models.Model):
    name = models.CharField(unique=False, max_length=200)
    image = models.ImageField(upload_to='screens/',
                              verbose_name='скрин')
    incoming_time = models.DateTimeField('Время добавления в базу', auto_now=True)
    worker = models.CharField(max_length=50, null=True)
    transaction = models.IntegerField('Транзакция', null=True, unique=True, blank=True)
    type = models.CharField(max_length=20, default='unknown')


class Deposit(models.Model):
    uid = models.CharField(max_length=36, db_index=True, unique=True, null=True, blank=True)
    register_time = models.DateTimeField('Время добавления в базу', auto_now=True)
    phone = models.CharField('Телефон отправителя')
    pay_sum = models.IntegerField('Сумма платежа', validators=[MinValueValidator(5)])
    input_transaction = models.IntegerField('Номер транзакции из чека', null=True, blank=True)
    status = models.CharField('Статус депозита', default='pending')
    pay_screen = models.ImageField(upload_to='pay_screens/',
                                   verbose_name='Чек об оплате', null=True, blank=True)


@receiver(post_delete, sender=BadScreen)
def screen_image_delete(sender, instance, **kwargs):
    if instance.image.name:
        instance.image.delete(False)


@receiver(post_delete, sender=Incoming)
def screen_image_delete(sender, instance, **kwargs):
    if instance.image.name:
        instance.image.delete(False)
