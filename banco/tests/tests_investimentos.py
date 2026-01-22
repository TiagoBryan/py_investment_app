from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.contrib.messages import get_messages


class InvestimentosFrontendTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Mock de sessão autenticada
        session = self.client.session
        session['auth_token'] = 'fake-token-xyz'
        session.save()
        
        # Login de usuário dummy para passar no @login_required/dispatch
        from django.contrib.auth import get_user_model
        self.user = get_user_model().objects.create(username='dummy', 
                                                    email='dummy@t.com')
        self.client.force_login(self.user)

    # --- teste dashboar (matematica) ---
    @patch('banco.views.investimentos_front_end.requests.get')
    def test_dashboard_calculo_projecao(self, mock_get):
        def side_effect(url, headers):
            if '/internal/clientes/' in url:
                class MockResp:  # type: ignore
                    status_code = 200

                    def json(self): 
                        return [{'id': 'uid-1', 
                                 'perfil_investidor': 'CONSERVADOR'}]
                return MockResp()
            
            if '/conta/score/' in url:
                class MockResp:  # type: ignore
                    status_code = 200
                    def json(self): return {'saldo': 1000.00}
                return MockResp()

            if '/internal/investimentos/cliente/' in url:
                class MockResp:
                    status_code = 200

                    def json(self): return [
                        {'valor_investido': 500.00, 'ativo': True},
                        {'valor_investido': 200.00, 'ativo': False} 
                    ]
                return MockResp()
            return None

        mock_get.side_effect = side_effect

        response = self.client.get(reverse('investimentos_dashboard_page'))
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.context['patrimonio_total'], 1500.00)
        
        self.assertEqual(response.context['projecao'], 1620.00)

    # --- teste cria investimento ---
    @patch('banco.views.investimentos_front_end.requests.post')
    @patch('banco.views.investimentos_front_end.get_cliente_investidor_id')
    def test_realizar_investimento_sucesso(self, mock_get_id, mock_post):
        mock_get_id.return_value = 'uid-1'
        mock_post.return_value.status_code = 201

        url = reverse('realizar_investimento_page')
        data = {'tipo_investimento': 'ACOES', 'valor_investido': '100.00'}

        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('listar_investimentos_page'))

    @patch('banco.views.investimentos_front_end.requests.post')
    @patch('banco.views.investimentos_front_end.get_cliente_investidor_id')
    def test_realizar_investimento_erro_saldo(self, mock_get_id, mock_post):
        """Se a API retornar erro (lista de strings), o form deve exibir"""
        mock_get_id.return_value = 'uid-1'
        mock_post.return_value.status_code = 400
        mock_post\
            .return_value.json.return_value = ["Saldo insuficiente na conta."]

        url = reverse('realizar_investimento_page')
        data = {'tipo_investimento': 'ACOES', 'valor_investido': '100000.00'}

        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        
        form = response.context['form']
        self.assertIn("Saldo insuficiente na conta.", form.non_field_errors())

    # --- teste desativar perfil (com bloqueio) ---
    @patch('banco.views.investimentos_front_end.requests.delete')
    @patch('banco.views.investimentos_front_end.get_cliente_investidor_id')
    def test_desativar_perfil_bloqueado(self, mock_get_id, mock_delete):
        mock_get_id.return_value = 'uid-1'
        
        # Simula erro 400 da API (investimentos ativos)
        mock_delete.return_value.status_code = 400
        mock_delete.return_value\
            .json.return_value = ["Existem investimentos ativos."]

        url = reverse('desativar_perfil_investidor_page')
        
        response = self.client.post(url)
        
        self.assertRedirects(response, 
                             reverse('atualizar_perfil_investidor_page'))
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Existem investimentos ativos.")