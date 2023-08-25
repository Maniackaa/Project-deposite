from django.db import models


class Incoming(models.Model):
    register_date = models.DateTimeField('Время добавления в базу', auto_now=True)
    response_date = models.DateTimeField('Распознанное время', null=True)
    sender = models.CharField('Отравитель/карта', max_length=50, null=True)
    bank = models.CharField(max_length=50, null=True)
    pay = models.FloatField('Платеж')
    balance = models.FloatField('Баланс', null=True)
    transaction = models.CharField('Транзакция', max_length=30, null=True)
    type = models.CharField(max_length=20, default='unknown')
