from django import forms


class DepositoForm(forms.Form):
    valor = forms.DecimalField(
        min_value=0.01,
        max_digits=15,
        decimal_places=2,
        label="Valor do depósito"
    )


class SaqueForm(forms.Form):
    valor = forms.DecimalField(
        min_value=0.01,
        max_digits=15,
        decimal_places=2,
        label="Valor do saque"
    )
