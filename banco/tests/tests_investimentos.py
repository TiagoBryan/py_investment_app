from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.contrib.messages import get_messages


class InvestimentosFrontendTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['auth_token'] = 'fake-token-xyz'
        session.save()
        
        from django.contrib.auth import get_user_model
        self.user = get_user_model().objects.create(username='dummy', 
                                                    email='dummy@t.com')
        self.client.force_login(self.user)

    # --- teste dashborad (matematica) ---
    @patch('banco.views.investimentos_front_end.requests.get')
    def test_dashboard_calculo_projecao(self, mock_get):
        """
        Verifica se o dashboard aplica a taxa sobre o total investido em renda,
        fixa ignorando o saldo da conta corrente na projeção.
        """
        def side_effect(url, headers):
            if '/internal/clientes/' in url:
                class MockResp:  # type: ignore
                    status_code = 200

                    def json(self): 
                        return [{'id': 'uid-1', 
                                 'perfil_investidor': 'CONSERVADOR'}]
                return MockResp()
            
            if 'score' in url:
                class MockResp:  # type: ignore
                    status_code = 200
                    def json(self): return {'saldo': 1000.00}
                return MockResp()

            if '/internal/investimentos/cliente/' in url:
                class MockResp:
                    status_code = 200

                    def json(self): return [
                        {'valor_investido': 500.00, 
                         'ativo': True, 'tipo_investimento': 'RENDA_FIXA'},
                        {'valor_investido': 200.00, 
                         'ativo': False, 'tipo_investimento': 'RENDA_FIXA'} 
                    ]
                return MockResp()
            
            return None

        mock_get.side_effect = side_effect

        response = self.client.get(reverse('investimentos_dashboard_page'))
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.context['total_investido'], 500.00)
        
        self.assertEqual(response.context['patrimonio_total'], 1500.00)

        self.assertEqual(response.context['projecao'], 540.00)

    # --- teste crira investimento (Formulário Novo) ---
    @patch('banco.views.investimentos_front_end.requests.post')
    @patch('banco.views.investimentos_front_end.get_cliente_investidor_id')
    def test_realizar_investimento_sucesso(self, mock_get_id, mock_post):
        mock_get_id.return_value = 'uid-1' 
        mock_post.return_value.status_code = 201 
        mock_post.return_value.json.return_value = {'id': '1', 
                                                    'valor_investido': 500}

        url = reverse('realizar_investimento_page')
        
        data = {
            'tipo_investimento': 'ACOES', 
            'ticker': 'PETR4',
            'quantidade': '10',
            'valor_investido': ''
        }

        response = self.client.post(url, data)
        
        self.assertRedirects(response, reverse('listar_investimentos_page'))

    @patch('banco.views.investimentos_front_end.requests.get')
    @patch('banco.views.investimentos_front_end.requests.post')
    @patch('banco.views.investimentos_front_end.get_cliente_investidor_id')
    def test_realizar_investimento_erro_saldo(self, mock_get_id, mock_post, 
                                              mock_get):
        """Se a API retornar erro, o form deve ser renderizado novamente 
        com o erro"""
        mock_get_id.return_value = 'uid-1'

        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = [
            "Saldo insuficiente na conta."]

        def side_effect_get(url, headers):
            if '/contas/' in url:
                class MockResp:
                    status_code = 200
                    def json(self): return {'saldo': 50.00}
                return MockResp()
            return None
        mock_get.side_effect = side_effect_get

        url = reverse('realizar_investimento_page')
        
        data = {
            'tipo_investimento': 'ACOES', 
            'ticker': 'BTC-USD',
            'quantidade': '1000'
        }

        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        
        form = response.context['form']
        self.assertIn("Saldo insuficiente na conta.", form.non_field_errors())
        
        self.assertEqual(response.context['conta']['saldo'], 50.00)

    # --- teste desativar perfil (Com bloqueio) ---
    @patch('banco.views.investimentos_front_end.requests.delete')
    @patch('banco.views.investimentos_front_end.get_cliente_investidor_id')
    def test_desativar_perfil_bloqueado(self, mock_get_id, mock_delete):
        """
        Teste da funcionalidade que redireciona de volta para a edição
        se houver erro na exclusão.
        """
        mock_get_id.return_value = 'uid-1'
        
        mock_delete.return_value.status_code = 400
        mock_delete.return_value.json.return_value = [
            "Existem investimentos ativos."]

        url = reverse('desativar_perfil_investidor_page')
        
        response = self.client.post(url)
        
        self.assertRedirects(response, 
                             reverse('atualizar_perfil_investidor_page'))
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Existem investimentos ativos", str(messages[0]))