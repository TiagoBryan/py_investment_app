from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch


class FrontendViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['auth_token'] = 'fake-token-123'
        session.save()

    # --- TESTE DE LOGIN (POST) ---
    @patch('banco.views.login_front_end.requests.post')
    @patch('banco.views.login_front_end.requests.get')
    def test_login_sucesso(self, mock_get, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'token': 'new-token-abc'}

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'first_name': 'Test',
                                                   'last_name': 'User'}

        url = reverse('login_page')
        data = {'email': 't@t.com', 'password': '123',
                'cpf_cnpj': '12345678900'}

        response = self.client.post(url, data)

        self.assertRedirects(response, reverse('home_page'))
        self.assertEqual(self.client.session['auth_token'], 'new-token-abc')

    @patch('banco.views.login_front_end.requests.post')
    def test_login_api_fora_do_ar(self, mock_post):
        """Se a API estiver offline, deve exibir erro tratado"""
        from requests import RequestException

        mock_post.side_effect = RequestException("Conexão recusada")

        url = reverse('login_page')
        data = {'email': 't@t.com', 'password': '123',
                'cpf_cnpj': '12345678900'}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        # Verifica se renderizou o template com o erro
        self.assertContains(response, "Erro de conexão com o servidor")

    # --- TESTE DE DEPÓSITO (POST) ---
    @patch('banco.views.movimentacao_front_end.requests.post')
    def test_deposito_sucesso(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value\
            .json.return_value = {'detail': 'Depósito realizado'}

        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create(username='dummy',
                                               email='dummy@t.com')
        self.client.force_login(user)

        url = reverse('deposito_page')
        data = {'valor': '50.00'}
        response = self.client.post(url, data)

        self.assertRedirects(response, reverse('home_page'))
        self.assertTrue(mock_post.called)

    # --- TESTE DE SAQUE (GET CONTEXTO) ---
    @patch('banco.views.movimentacao_front_end.requests.get')
    def test_saque_exibe_saldo(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'saldo': 500.00,
                                                   'score_credito': 50.0}

        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create(username='dummy2',
                                               email='d2@t.com')
        self.client.force_login(user)

        response = self.client.get(reverse('saque_page'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['saldo'], 500.00)

    # --- TESTE DE CADASTRO (ERRO DA API) ---
    @patch('banco.views.signup_front_end.requests.post')
    def test_signup_erro_email_duplicado(self, mock_post):
        # Simula API retornando 400 Bad Request
        mock_post.return_value.status_code = 400
        # Simula o JSON que o DRF/Authemail retorna
        mock_post.return_value.text = '{"detail": "Email já cadastrado"}'
        mock_post.return_value.json\
            .return_value = {'detail': 'Email já cadastrado'}

        url = reverse('signup_page')
        data = {
            'first_name': 'A', 'last_name': 'B', 'email': 'existente@t.com',
            'password': 'senhaforte369', 'confirm_password': 'senhaforte369',
            'tipo_pessoa': 'F', 'cpf_cnpj': '11122233344'
        }

        response = self.client.post(url, data)

        # Não redireciona, volta para o form com erro (Status 200)
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertIn('Email já cadastrado', form.non_field_errors())
