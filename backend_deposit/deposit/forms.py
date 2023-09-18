import datetime
import logging

from django import forms
from django.core.exceptions import ValidationError

from backend_deposit.settings import TZ
from .models import Deposit

logger = logging.getLogger(__name__)


class DepositForm(forms.ModelForm):
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        cleaned_phone = ''
        for num in phone:
            if num.isdigit() or num in '+':
                cleaned_phone += num
        if not cleaned_phone.startswith('+994'):
            raise ValidationError('Телефон должен начинаться с +994')
        if len(cleaned_phone) != 11:
            raise ValidationError('Неверное количество цифр в телефоне')
        # current_time = datetime.datetime.now(tz=TZ)
        # time_threshold = current_time - datetime.timedelta(minutes=5)
        # logger.debug(f'дельта {str(time_threshold)}')
        # last_pay_from_phone = Deposit.objects.filter(register_time__gte=time_threshold, phone=cleaned_phone).exists()
        # logger.debug(f'last_pay_from_phone {last_pay_from_phone}')
        # if last_pay_from_phone:
        #     logger.debug(f'Повтороное создание')
        #     raise ValidationError('Вы уже создавали платеж')

        return cleaned_phone

    uid = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Deposit
        fields = ('phone', 'pay_sum', 'uid')
        hidden_fields = ('uid',)
        help_texts = {'phone': 'Ваш телефон',
                      'pay_sum': 'Сумма платежа'}
        labels = {'phone': 'Your phone', 'pay_sum': 'Pay summ (Min: 5 AZN, Max: Unlim)'}


class DepositImageForm(forms.ModelForm):
    uid = forms.CharField(widget=forms.HiddenInput)
    phone = forms.CharField(widget=forms.HiddenInput)
    pay_sum = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = Deposit
        fields = ('uid', 'phone', 'pay_sum', 'uid', 'pay_screen')
        # exclude = ('phone', 'pay_sum', 'uid',)
        hidden_fields = ('uid', 'phone', 'pay_sum', )
