
import logging

from django import forms
from django.core.exceptions import ValidationError


from .models import Deposit, Incoming

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
        if len(cleaned_phone) != 13:
            raise ValidationError('Неверное количество цифр в телефоне')
        return cleaned_phone

    uid = forms.CharField(widget=forms.HiddenInput)
    input_transaction = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Deposit
        fields = ('phone', 'pay_sum', 'uid')
        hidden_fields = ('uid',  'input_transaction')
        help_texts = {'phone': 'Ваш телефон',
                      'pay_sum': 'Сумма платежа'}
        labels = {'phone': 'Your phone', 'pay_sum': 'Pay summ (Min: 5 AZN, Max: Unlim)'}


class DepositEditForm(forms.ModelForm):
    uid = forms.Field(disabled=True)
    phone = forms.Field(disabled=True)
    pay_sum = forms.Field(disabled=True)
    input_transaction = forms.Field(disabled=True)
    confirmed_incoming = forms.ModelChoiceField(
        queryset=None,
        blank=True,
        required=False,
    )
    status = forms.CharField(widget=forms.HiddenInput, disabled=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        deposit: Deposit = kwargs.get('instance')
        incoming_id = None
        if deposit.confirmed_incoming:
            incoming_id = deposit.confirmed_incoming.id
        self.fields['confirmed_incoming'].queryset = Incoming.objects.filter(confirmed_deposit=None).order_by('-id') | Incoming.objects.filter(id=incoming_id)

    class Meta:
        model = Deposit
        fields = ('input_transaction', 'pay_sum', 'phone', 'uid', 'confirmed_incoming', )
        hidden_fields = ('pay_screen',)


class DepositImageForm(forms.ModelForm):
    uid = forms.CharField(widget=forms.HiddenInput, disabled=True)
    phone = forms.CharField(widget=forms.HiddenInput, disabled=True)
    pay_sum = forms.IntegerField(widget=forms.HiddenInput, disabled=True)
    input_transaction = forms.IntegerField(widget=forms.HiddenInput, disabled=True)

    class Meta:
        model = Deposit
        fields = ('uid', 'phone', 'pay_sum', 'uid', 'pay_screen', 'input_transaction')
        # exclude = ('phone', 'pay_sum', 'uid',)
        hidden_fields = ('uid', 'phone', 'pay_sum', 'input_transaction')
        labels = {'pay_screen': '', 'input_transaction': 'Номер тарнзакции'}
        # help_texts = {'pay_screen': 'pay_screen',
        #               'input_transaction': 'input_transaction'}


class DepositTransactionForm(forms.ModelForm):
    uid = forms.CharField(widget=forms.HiddenInput)
    phone = forms.CharField(widget=forms.HiddenInput)
    pay_sum = forms.CharField(widget=forms.HiddenInput)
    input_transaction = forms.IntegerField(required=False, min_value=50_000_000, max_value=99_999_999)

    class Meta:
        model = Deposit
        fields = ('uid', 'phone', 'pay_sum', 'uid', 'input_transaction')
        hidden_fields = ('uid', 'phone', 'pay_sum')
        labels = {'pay_screen': '', 'input_transaction': 'Номер тарнзакции'}
