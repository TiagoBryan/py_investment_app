from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=255, label="E-mail")
    cpf_cnpj = forms.CharField(max_length=18, label="CPF/CNPJ")
    password = forms.CharField(max_length=128, widget=forms.PasswordInput, 
                               label="Senha")

    def clean_cpf_cnpj(self):
        value = self.cleaned_data['cpf_cnpj']
        return value.replace('.', '').replace('-', '').replace('/', '')