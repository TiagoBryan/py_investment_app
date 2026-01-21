from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from banco.forms import RealizarInvestimentoForm


class InvestimentosFrontendTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['auth_token'] = 'fake-token'
        session.save()

    def test_form_investimento_valido(self):
        form = RealizarInvestimentoForm(data={
            'tipo_investimento': 'ACOES',
            'valor_investido': '100.00'
        })
        self.assertTrue(form.is_valid())

    def test_form_investimento_valor_negativo(self):
        form = RealizarInvestimentoForm(data={
            'tipo_investimento': 'ACOES',
            'valor_investido': '-50.00'
        })
        self.assertFalse(form.is_valid())

    @patch('banco.views.investimentos_front_end.requests.post')
    @patch('banco.views.investimentos_front_end.get_cliente_investidor_id')
    def test_realizar_investimento_view(self, mock_get_id, mock_post):
        # Simula ID do cliente encontrado
        mock_get_id.return_value = 'uuid-fake-123'

        # Simula API retornando 201 Created
        mock_post.return_value.status_code = 201

        # loga um usuário dummy no django
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create(username='dummy',
                                               email='dummy@t.com')
        self.client.force_login(user)

        url = reverse('realizar_investimento_page')
        data = {'tipo_investimento': 'CRIPTO', 'valor_investido': '200.00'}

        response = self.client.post(url, data)

        self.assertRedirects(response, reverse('listar_investimentos_page'))
        self.assertTrue(mock_post.called)

    @patch('banco.views.investimentos_front_end.requests.get')
    def test_dashboard_calculo_patrimonio_e_projecao(self, mock_get):
        """
        Verifica se o Dashboard soma Saldo + Investimentos
        e aplica a taxa correta (CONSERVADOR = 8%).
        """
        # O mock deve retornar valores diferentes para cada chamada de URL
        def side_effect(url, headers):
            # 1. Chamada de Perfil
            if '/internal/clientes/' in url:
                class MockResponse:  # type: ignore
                    status_code = 200

                    def json(self):
                        return [{
                            'id': 'uuid-123',
                            'perfil_investidor': 'CONSERVADOR'
                        }]
                return MockResponse()

            # 2. Chamada de Saldo Bancário
            if '/conta/score/' in url:
                class MockResponse:  # type: ignore
                    status_code = 200

                    def json(self):
                        return {'saldo': 1000.00}  # Tem 1000 na conta
                return MockResponse()

            # 3. Chamada de Investimentos
            if '/internal/investimentos/cliente/' in url:
                class MockResponse:
                    status_code = 200

                    def json(self):
                        return [
                            {'valor_investido': 500.00, 'ativo': True},
                            {'valor_investido': 200.00,
                             'ativo': False}  # Inativo não deve somar
                        ]
                return MockResponse()

            return None

        mock_get.side_effect = side_effect

        # Login dummy
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create(username='dummy2',
                                               email='d2@t.com')
        self.client.force_login(user)

        response = self.client.get(reverse('investimentos_dashboard_page'))

        self.assertEqual(response.status_code, 200)

        # VERIFICAÇÕES MATEMÁTICAS

        # 1. Total Investido (Apenas o ativo: 500)
        self.assertEqual(response.context['total_investido'], 500.00)

        # 2. Saldo Conta (1000)
        self.assertEqual(response.context['saldo_conta'], 1000.00)

        # 3. Patrimônio Total (1000 + 500 = 1500)
        self.assertEqual(response.context['patrimonio_total'], 1500.00)

        # 4. Projeção (Conservador 8% a.a.)
        # 1500 * 1.08 = 1620
        self.assertEqual(response.context['projecao'], 1620.00)
