import requests
from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import redirect


class LandingFrontEnd(TemplateView):
    template_name = 'exibicao_templates/landing.html'


class HomeFrontEnd(TemplateView):
    template_name = 'exibicao_templates/home.html'

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
            url_user = f"{settings.API_BASE_URL}/users/me/"
            resp_user = requests.get(url_user, headers=headers)
            
            if resp_user.status_code == 200:
                user_data = resp_user.json()
                context['first_name'] = user_data.get('first_name')
                context['last_name'] = user_data.get('last_name')
                context['email'] = user_data.get('email')
        except requests.RequestException:
            pass

        context['conta'] = None
        context['conta_id'] = None
        
        try:
            url_conta = f"{settings.API_BASE_URL}/contas/"
            resp_conta = requests.get(url_conta, headers=headers)

            if resp_conta.status_code == 200:
                conta_data = resp_conta.json()
                
                if conta_data.get('ativa') is True:
                    context['conta'] = conta_data
                    context['conta_id'] = conta_data.get('id')
                else:
                    context['conta'] = None
                    context['conta_id'] = None
                
        except requests.RequestException:
            pass

        return context


class ScoreCreditoFrontEnd(TemplateView):
    template_name = "exibicao_templates/score.html"

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

        url = f"{settings.API_BASE_URL}/conta/score/"

        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                context["saldo"] = data.get("saldo")
                context["score"] = data.get("score_credito")
            else:
                context["error"] = "Não foi possível calcular o score no " \
                                    "momento."
                context["saldo"] = "---"
                context["score"] = "---"

        except requests.RequestException:
            context["error"] = "Erro de conexão."
            context["saldo"] = "---"
            context["score"] = "---"

        return context


class DashboardInvestimentosFrontEnd(TemplateView):
    template_name = "investimentos_templates/dashboard.html"
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_page')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.request.session.get('auth_token')
        headers = {'Authorization': f'Token {token}'}

        saldo_conta = 0.0
        total_investido = 0.0
        patrimonio_total = 0.0
        meu_perfil = None

        try:
            url_perfil = f"{settings.API_BASE_URL}/internal/clientes/" 
            resp_perfil = requests.get(url_perfil, headers=headers)
                     
            if resp_perfil.status_code == 200:
                clientes = resp_perfil.json()
                if clientes:
                    meu_perfil = clientes[0]
                    context['investidor'] = meu_perfil
                    
                    cliente_id = meu_perfil['id']

                    base = settings.API_BASE_URL

                    url_saldo = f"{base}/conta/score/"
                    try:
                        resp_saldo = requests.get(url_saldo, headers=headers)
                        if resp_saldo.status_code == 200:
                            saldo_conta = float(resp_saldo.json().get('saldo', 
                                                                      0))
                    except Exception:
                        saldo_conta = 0.0
                    
                    base = f"{settings.API_BASE_URL}/internal/investimentos/"

                    url_inv = f"{base}cliente/{cliente_id}/"
                    try:
                        resp_inv = requests.get(url_inv, headers=headers)
                        if resp_inv.status_code == 200:
                            investimentos = resp_inv.json()
                            total_investido = sum(float(i['valor_investido']) 
                                                  for i in investimentos if 
                                                  i.get('ativo', True))
                    except Exception:
                        total_investido = 0.0

                    patrimonio_total = saldo_conta + total_investido

                    perfil_tipo = meu_perfil.get('perfil_investidor', 
                                                 'CONSERVADOR')
                    if perfil_tipo == 'CONSERVADOR':
                        taxa = 0.08
                    elif perfil_tipo == 'MODERADO':
                        taxa = 0.12
                    else:
                        taxa = 0.18
                    
                    context['projecao'] = patrimonio_total * (1 + taxa)

        except Exception as e:
            print(f"Erro no dashboard: {e}")
            context['error'] = "Serviço de investimentos indisponível no " \
                               "momento."
        
        context['saldo_conta'] = saldo_conta
        context['total_investido'] = total_investido
        context['patrimonio_total'] = patrimonio_total
            
        return context