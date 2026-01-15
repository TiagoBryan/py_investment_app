from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=150, label='Nome', required=True)
    last_name = forms.CharField(max_length=150, label='Sobrenome', 
                                required=True)
    email = forms.EmailField(max_length=255, label='E-mail', required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
    
    password = forms.CharField(
        label='Senha', 
        widget=forms.PasswordInput,
        min_length=8
    )
    confirm_password = forms.CharField(
        label='Confirmar Senha', 
        widget=forms.PasswordInput
    )

    TIPO_PESSOA_CHOICES = [
        ('F', _('Pessoa Física')),
        ('J', _('Pessoa Jurídica')),
    ]
    tipo_pessoa = forms.ChoiceField(choices=TIPO_PESSOA_CHOICES, label='Tipo')
    cpf_cnpj = forms.CharField(max_length=18, label='CPF/CNPJ')

    def clean_cpf_cnpj(self):
        value = self.cleaned_data['cpf_cnpj']
        return value.replace('.', '').replace('-', '').replace('/', '')

    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        if password:
            try:
                validate_password(password, user=self.user)
            except ValidationError as e:
                raise forms.ValidationError(e.messages)  # type: ignore
        
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "As senhas não conferem.")
        
        return cleaned_data