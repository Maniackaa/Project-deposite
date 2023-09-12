from django.db import models
from django.dispatch import receiver

from django.db.models.signals import post_delete


class Incoming(models.Model):
    register_date = models.DateTimeField('Время добавления в базу', auto_now=True)
    response_date = models.DateTimeField('Распознанное время', null=True)
    recipient = models.CharField('Получатель', max_length=50, null=True)
    sender = models.CharField('Отравитель/карта', max_length=50, null=True)
    pay = models.FloatField('Платеж')
    balance = models.FloatField('Баланс', null=True)
    transaction = models.IntegerField('Транзакция', null=True, unique=True)
    type = models.CharField(max_length=20, default='unknown')
    worker = models.CharField(max_length=50, null=True)


class Screen(models.Model):
    name = models.CharField(unique=False, max_length=200)
    image = models.ImageField(upload_to='screens/',
                              verbose_name='скрин')
    incoming_time = models.DateTimeField('Время добавления в базу', auto_now=True)
    status = models.CharField(max_length=20, null=True)


@receiver(post_delete, sender=Screen)
def screen_image_delete(sender, instance, **kwargs):
    if instance.image.name:
        instance.image.delete(False)
