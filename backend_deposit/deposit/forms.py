from django import forms
from django.core.exceptions import ValidationError

from .models import Deposit


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
        return cleaned_phone

    class Meta:
        model = Deposit
        fields = ('phone', 'pay_sum')
        help_texts = {'phone': 'Ваш телефон',
                      'pay_sum': 'Сумма платежа'}
        labels = {'phone': 'Your phone', 'pay_sum': 'Pay summ (Min: 5 AZN, Max: Unlim)'}
