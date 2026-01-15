from django.test import TestCase
from banco.forms import (
    LoginForm,
    DepositoForm,
    SignupForm,
    UsersMeChangeForm,
)


class FrontendFormsTest(TestCase):

    def test_login_limpeza_cpf(self):
        form = LoginForm(data={
            'email': 'teste@teste.com',
            'cpf_cnpj': '123.456.789-00',
            'password': 'senha123'
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['cpf_cnpj'], '12345678900')

    def test_signup_senhas_conferem(self):
        form = SignupForm(data={
            'first_name': 'João',
            'last_name': 'Silva',
            'email': 'joao@teste.com',
            'tipo_pessoa': 'F',
            'cpf_cnpj': '111.222.333-44',
            'password': 'senha369',
            'confirm_password': 'senha369'
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['cpf_cnpj'], '11122233344')

    def test_signup_senhas_diferentes(self):
        form = SignupForm(data={
            'first_name': 'João',
            'last_name': 'Silva',
            'email': 'joao@teste.com',
            'tipo_pessoa': 'F',
            'cpf_cnpj': '111.222.333-44',
            'password': 'senha369',
            'confirm_password': 'senha456'  # Diferente
        })
        self.assertFalse(form.is_valid())
        self.assertIn('confirm_password', form.errors)

    def test_deposito_valor_negativo(self):
        form = DepositoForm(data={'valor': '-10.00'})
        self.assertFalse(form.is_valid())

    def test_users_me_change(self):
        form = UsersMeChangeForm(data={'first_name': 'Novo',
                                       'last_name': 'Nome'})
        self.assertTrue(form.is_valid())
