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
from banco.forms import RealizarInvestimentoForm
from django.http import Http404


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
            context['error'] = "Perfil de investidor não encontrado."
            return context
        
        base = settings.API_BASE_URL
        url = f"{base}/internal/investimentos/cliente/{cliente_id}/"

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                investimentos = response.json()
                context['investimentos'] = investimentos
                
                total = sum(float(item['valor_investido']) 
                            for item in investimentos if item['ativo'])
                context['total_investido'] = total
            else:
                context['error'] = "Não foi possível carregar os " \
                                   "investimentos."
        except requests.RequestException:
            context['error'] = "Erro de conexão com o servidor."

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
                           "Você precisa criar um perfil de investidor antes.")
            return redirect('criar_perfil_investidor_page')

        payload = {
            'cliente': cliente_id,
            'tipo_investimento': form.cleaned_data['tipo_investimento'],
            'valor_investido': float(form.cleaned_data['valor_investido']),
            'ativo': True
        }

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
            messages.success(self.request, 
                             "Investimento realizado com sucesso!")
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
                            if isinstance(msgs, list):
                                for msg in msgs:
                                    form.add_error(field, msg)
                            else:
                                form.add_error(field, msgs)
                        else:
                            form.add_error(None, f"{msgs}")
            
            except Exception as e:
                print(f"Erro ao processar JSON: {e}")
                form.add_error(None, 
                               "Erro ao processar a resposta do servidor.")
            
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