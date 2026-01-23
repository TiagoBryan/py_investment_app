import requests
from django.http import JsonResponse
from django.conf import settings
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from banco.forms import CriarPerfilInvestidorForm
from banco.forms import RealizarInvestimentoForm, AtualizarPerfilInvestidorForm
from django.http import Http404
import json


class MarketDataAjaxView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        token = request.session.get('auth_token')
        headers = {'Authorization': f'Token {token}'}
        
        params = request.GET.copy()
        
        url = f"{settings.API_BASE_URL}/internal/market/"

        try:
            response = requests.get(url, headers=headers, params=params, 
                                    timeout=5)
            
            return JsonResponse(response.json(), status=response.status_code)
            
        except requests.RequestException:
            return JsonResponse({'error': 'Erro de comunicação com a API'}, 
                                status=503)


class ProjecaoRetornoFrontEnd(View):
    def get(self, request, cliente_id):
        token = request.session.get('auth_token')
        headers = {'Authorization': f'Token {token}'}
        
        url = f"{settings.API_BASE_URL}/internal/clientes/{cliente_id}/"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return JsonResponse({'error': 'Cliente não encontrado'}, 
                                    status=404)
            
            data = response.json()
            
            perfil = data.get('perfil_investidor')
            patrimonio = float(data.get('patrimonio_total', 0))
            
            taxa = 0.0
            
            if perfil == 'CONSERVADOR':
                taxa = 0.08
            elif perfil == 'MODERADO':
                taxa = 0.12
            elif perfil == 'ARROJADO':
                taxa = 0.18
            
            lucro_projetado = patrimonio * taxa
            total_projetado = patrimonio + lucro_projetado
            
            return JsonResponse({
                'cliente_id': cliente_id,
                'perfil': perfil,
                'patrimonio_atual': patrimonio,
                'taxa_aplicada': f"{taxa*100}%",
                'lucro_projetado_1_ano': lucro_projetado,
                'patrimonio_projetado_1_ano': total_projetado
            })

        except requests.RequestException:
            return JsonResponse(
                {'error': 'Erro de comunicação com Data Service'}, status=503)
        

class CriarPerfilInvestidorFrontEnd(FormView):
    template_name = "investimentos_templates/criar_perfil.html"
    form_class = CriarPerfilInvestidorForm
    success_url = reverse_lazy("investimentos_dashboard_page")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_page')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        token = self.request.session.get('auth_token')
        
        payload = {
            'perfil_investidor': form.cleaned_data['perfil_investidor'],
            'patrimonio_total': float(form.cleaned_data['patrimonio_total'])
        }

        url = f"{settings.API_BASE_URL}/internal/clientes/" 
        
        headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
        except requests.RequestException:
            form.add_error(None, "Erro de conexão com o servidor de "
                                 "investimentos.")
            return self.form_invalid(form)

        if response.status_code == 201:
            messages.success(self.request, 
                             "Perfil de investidor criado com sucesso!")
            return super().form_valid(form)
        
        elif response.status_code == 400:
            try:
                errors = response.json()
                if 'detail' in errors:
                    form.add_error(None, errors['detail'])
                if 'pessoa' in errors:
                    form.add_error(None, 
                                   "Você já possui um perfil de investidor "
                                   "criado.")
                
                for field, msgs in errors.items():
                    if field in form.fields:
                        for msg in msgs:
                            form.add_error(field, msg)
            except Exception as e:
                form.add_error(e, "Erro ao processar dados.")
            return self.form_invalid(form)
        
        else:
            form.add_error(None, f"Erro inesperado: {response.status_code}")
            return self.form_invalid(form)


def get_cliente_investidor_id(request):
    token = request.session.get('auth_token')
    headers = {'Authorization': f'Token {token}'}
    
    url = f"{settings.API_BASE_URL}/internal/clientes/"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            clientes = response.json()
            if clientes and len(clientes) > 0:
                return clientes[0]['id']
    except Exception:
        pass
    return None


class ListarInvestimentosFrontEnd(TemplateView):
    template_name = "investimentos_templates/listar_investimentos.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_page')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.request.session.get('auth_token')
        headers = {'Authorization': f'Token {token}'}

        cliente_id = get_cliente_investidor_id(self.request)
        if not cliente_id:
            context['error'] = "Perfil não encontrado."
            return context

        base = settings.API_BASE_URL
        url_lista = f"{base}/internal/investimentos/cliente/{cliente_id}/"

        try:
            resp_lista = requests.get(url_lista, headers=headers)
            if resp_lista.status_code == 200:
                investimentos = resp_lista.json()
                context['investimentos'] = investimentos
                context['total_investido'] = sum(float(i['valor_investido']) 
                                                 for i in investimentos if 
                                                 i.get('ativo'))
        except Exception:
            context['error'] = "Erro ao buscar investimentos."

        url_analytics = f"{base}/internal/analytics/cliente/{cliente_id}/"

        periodo_selecionado = self.request.GET.get('periodo', '1y')
        
        validos = ['1mo', '3mo', '6mo', '1y', '2y', '5y', 'max']
        if periodo_selecionado not in validos:
            periodo_selecionado = '1y'

        try:
            resp_analytics = requests.get(url_analytics, headers=headers, 
                                          params={
                                              'periodo': periodo_selecionado})
            
            if resp_analytics.status_code == 200:
                dados_analytics = resp_analytics.json()
                
                context['metrics'] = dados_analytics.get('metricas', {})
                
                historico = dados_analytics.get('historico', {})
                if historico and len(historico.get('datas', [])) > 1:
                    chart_data_js_friendly = {
                        "labels": historico.get('datas', []),
                        "portfolio": historico.get('carteira_pct', []),
                        "benchmark": historico.get('benchmark_pct', [])
                    }

                    chart_data_real = chart_data_js_friendly
                    context['chart_data'] = json.dumps(chart_data_real)
                    print("Entrou - Dados Formatados para JS")
                
            elif resp_analytics.status_code == 404:
                context['analytics_error'] = "Dados de análise ainda não "
                "disponíveis."
        
        except requests.RequestException:
            pass
        
        context['periodo_atual'] = periodo_selecionado
        return context


class RealizarInvestimentoFrontEnd(FormView):
    template_name = "investimentos_templates/realizar_investimento.html"
    form_class = RealizarInvestimentoForm
    success_url = reverse_lazy("listar_investimentos_page")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_page')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        token = self.request.session.get('auth_token')
        if not token:
            return context

        headers = {'Authorization': f'Token {token}'}

        try:
            response = requests.get(
                f"{settings.API_BASE_URL}/contas/", 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                context['conta'] = data
            else:
                raise Http404("Conta não encontrada na API.")

        except requests.RequestException:
            context['api_error'] = "Impossivel carregar os dados da conta."
        
        return context

    def form_valid(self, form):
        token = self.request.session.get('auth_token')
        cliente_id = get_cliente_investidor_id(self.request)
        
        if not cliente_id:
            messages.error(self.request, 
                           "Crie um perfil de investidor primeiro.")
            return redirect('criar_perfil_investidor_page')

        data = form.cleaned_data
        
        payload = {
            'cliente': cliente_id,
            'tipo_investimento': data['tipo_investimento'],
            'ativo': True
        }

        if data['tipo_investimento'] == 'RENDA_FIXA':
            payload['valor_investido'] = float(data['valor_investido'])
        else:
            payload['ticker'] = data['ticker'].upper()
            payload['quantidade'] = float(data['quantidade'])

        url = f"{settings.API_BASE_URL}/internal/investimentos/"
        headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
        except requests.RequestException:
            form.add_error(None, "Erro de conexão.")
            return self.form_invalid(form)

        if response.status_code == 201:
            dados_retorno = response.json()
            valor_final = dados_retorno.get('valor_investido', 0)
            ticker_final = dados_retorno.get('ticker', 'Renda Fixa')
            
            msg = f"Investimento realizado! Compra de {ticker_final}\
                  totalizando R$ {float(valor_final):.2f}"
            messages.success(self.request, msg)
            
            return super().form_valid(form)
        else:
            try:
                data = response.json()
                if isinstance(data, list):
                    for erro in data: 
                        form.add_error(None, erro)
                elif isinstance(data, dict):
                    if 'detail' in data: 
                        form.add_error(None, data['detail'])
                    for field, msgs in data.items():
                        if field == 'detail': 
                            continue
                        if field in form.fields:
                            ms = msgs if isinstance(msgs, list) else [msgs]
                            for m in ms: 
                                form.add_error(field, m)
                        else:
                            form.add_error(None, str(msgs))
            except Exception:
                form.add_error(None, "Erro desconhecido na API.")
            
            return self.form_invalid(form)


class ResgatarInvestimentoFrontEnd(View):
    def post(self, request, investimento_id):
        if not request.user.is_authenticated:
            return redirect('login_page')

        token = request.session.get('auth_token')
        headers = {'Authorization': f'Token {token}'}

        base = settings.API_BASE_URL

        url = f"{base}/internal/investimentos/{investimento_id}/"

        try:
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 204:
                messages.success(request, 
                                 "Investimento resgatado/cancelado com "
                                 "sucesso.")
            elif response.status_code == 404:
                messages.error(request, "Investimento não encontrado.")
            else:
                messages.error(request, "Erro ao tentar resgatar o "
                                        "investimento.")
                
        except requests.RequestException:
            messages.error(request, "Erro de conexão.")

        return redirect('listar_investimentos_page')
    

class AtualizarPerfilInvestidorFrontEnd(FormView):
    template_name = "investimentos_templates/atualizar_perfil.html"
    form_class = AtualizarPerfilInvestidorForm
    success_url = reverse_lazy("investimentos_dashboard_page")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_page')
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        token = self.request.session.get('auth_token')
        headers = {'Authorization': f'Token {token}'}
        
        cliente_id = get_cliente_investidor_id(self.request)
        if cliente_id:
            url = f"{settings.API_BASE_URL}/internal/clientes/{cliente_id}/"
            try:
                resp = requests.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    initial['perfil_investidor'] = data\
                        .get('perfil_investidor')
            except Exception:
                pass
        return initial

    def form_valid(self, form):
        token = self.request.session.get('auth_token')
        cliente_id = get_cliente_investidor_id(self.request)
        
        if not cliente_id:
            return redirect('home_page')

        url = f"{settings.API_BASE_URL}/internal/clientes/{cliente_id}/"
        headers = {'Authorization': f'Token {token}', 
                   'Content-Type': 'application/json'}
        
        payload = {
            'perfil_investidor': form.cleaned_data['perfil_investidor']
        }

        try:
            response = requests.patch(url, json=payload, headers=headers)
        except requests.RequestException:
            form.add_error(None, "Erro de conexão.")
            return self.form_invalid(form)

        if response.status_code == 200:
            messages.success(self.request, "Perfil atualizado com sucesso!")
            return super().form_valid(form)
        else:
            form.add_error(None, "Erro ao atualizar perfil.")
            return self.form_invalid(form)


class DesativarPerfilInvestidorFrontEnd(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login_page')

        token = request.session.get('auth_token')
        cliente_id = get_cliente_investidor_id(request)
        
        if not cliente_id:
            messages.error(request, "Perfil não encontrado.")
            return redirect('home_page')

        url = f"{settings.API_BASE_URL}/internal/clientes/{cliente_id}/"
        headers = {'Authorization': f'Token {token}'}

        try:
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 204:
                messages.success(request, 
                                 "Perfil de investidor cancelado com sucesso.")
                return redirect('home_page')
            
            elif response.status_code == 400:
                try:
                    data = response.json()
                    
                    msg = "Não foi possível realizar a operação."

                    if isinstance(data, list):
                        msg = data[0]
                    elif isinstance(data, dict):
                        if 'detail' in data:
                            msg = data['detail']
                        else:
                            first_val = next(iter(data.values()))
                            msg = first_val[0] if isinstance(first_val, list) \
                                else first_val
                    
                    messages.error(request, msg)
                except Exception as e:
                    print(f"Erro ao ler JSON de erro: {e}")
                    messages.error(request, 
                                   "Não foi possível cancelar o perfil devido "
                                   "a restrições.")
            
            else:
                messages.error(request, 
                               f"Erro inesperado: {response.status_code}")

        except requests.RequestException:
            messages.error(request, "Erro de conexão com o servidor.")

        return redirect('atualizar_perfil_investidor_page')
