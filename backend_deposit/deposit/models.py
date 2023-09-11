from django.db import models


class Incoming(models.Model):
    register_date = models.DateTimeField('Время добавления в базу', auto_now=True)
    response_date = models.DateTimeField('Распознанное время', null=True)
    recipient = models.CharField('Получатель', max_length=50, null=True)
    sender = models.CharField('Отравитель/карта', max_length=50, null=True)
    bank = models.CharField(max_length=50, null=True)
    pay = models.FloatField('Платеж')
    balance = models.FloatField('Баланс', null=True)
    transaction = models.IntegerField('Транзакция', null=True)
    type = models.CharField(max_length=20, default='unknown')
    message_url = models.CharField(max_length=100, null=True)


class Screen(models.Model):
    name = models.CharField(unique=False, max_length=200)
    image = models.ImageField(upload_to='screens/',
                              verbose_name='скрин')