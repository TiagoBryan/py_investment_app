from django import forms
from django.core.validators import RegexValidator


class ContaCorrenteForm(forms.Form):
    agencia = forms.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='A agência deve conter apenas números.'
            )
        ]
    )

    numero = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='O número da conta deve conter apenas números.'
            )
        ]
    )


class ContaCorrenteDeactivateForm(forms.Form):
    password = forms.CharField(
        label='Confirme sua senha',
        widget=forms.PasswordInput,
        max_length=128
    )
