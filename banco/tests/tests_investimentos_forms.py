from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from banco.forms import RealizarInvestimentoForm


class InvestimentoFormTest(TestCase):
    def test_validacao_renda_variavel(self):
        """acoes, ticker e quantidade sao obrigatorios, valor não"""
        form = RealizarInvestimentoForm(data={
            'tipo_investimento': 'ACOES',
            'ticker': 'PETR4',
            'quantidade': '10',
            'valor_investido': ''
        })
        self.assertTrue(form.is_valid())

        form_err = RealizarInvestimentoForm(data={
            'tipo_investimento': 'ACOES',
            'ticker': '',
            'quantidade': '10'
        })
        self.assertFalse(form_err.is_valid())
        self.assertIn('ticker', form_err.errors)

    def test_validacao_renda_fixa(self):
        """renda fixa o valor é obrigatório, ticker não"""
        form = RealizarInvestimentoForm(data={
            'tipo_investimento': 'RENDA_FIXA',
            'valor_investido': '1000.00',
            'ticker': '',
            'quantidade': ''
        })
        self.assertTrue(form.is_valid())

        form_err = RealizarInvestimentoForm(data={
            'tipo_investimento': 'RENDA_FIXA',
            'valor_investido': ''
        })
        self.assertFalse(form_err.is_valid())
        self.assertIn('valor_investido', form_err.errors)


class InvestimentoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['auth_token'] = 'fake-token'
        session.save()
        
        from django.contrib.auth import get_user_model
        self.user = get_user_model().objects.create(username='dummy', 
                                                    email='d@d.com')
        self.client.force_login(self.user)

    @patch('banco.views.investimentos_front_end.get_cliente_investidor_id')
    @patch('banco.views.investimentos_front_end.requests.post')
    def test_envio_payload_acoes(self, mock_post, mock_get_id):
        """
        Verifica se a View monta o JSON correto para acoes 
        """
        mock_get_id.return_value = 'uid-123'
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {
            'ticker': 'PETR4', 'valor_investido': 500
        }

        url = reverse('realizar_investimento_page')
        data = {
            'tipo_investimento': 'ACOES',
            'ticker': 'PETR4',
            'quantidade': '10',
            'valor_investido': ''
        }

        self.client.post(url, data)

        args, kwargs = mock_post.call_args
        payload_enviado = kwargs['json']

        self.assertEqual(payload_enviado['tipo_investimento'], 'ACOES')
        self.assertEqual(payload_enviado['ticker'], 'PETR4')
        self.assertEqual(payload_enviado['quantidade'], 10.0)
        self.assertNotIn('valor_investido', payload_enviado)

    @patch('banco.views.investimentos_front_end.requests.get')
    def test_ajax_proxy_quote(self, mock_get):
        """testa se a view AJAX repassa a chamada para a API"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'ticker': 'PETR4', 
                                                   'price': 38.00}

        url = reverse('ajax_market_data')
        response = self.client.get(url, {'action': 'quote', 'ticker': 'PETR4'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['price'], 38.00)
        
        args, kwargs = mock_get.call_args
        self.assertIn('/internal/market/', args[0])