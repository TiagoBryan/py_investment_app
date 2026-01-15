from django import forms


class UsersMeChangeForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Nome"
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Sobrenome"
    )


class UserDeactivateForm(forms.Form):
    password = forms.CharField(
        label="Confirme sua senha para continuar",
        widget=forms.PasswordInput,
        max_length=128
    )
