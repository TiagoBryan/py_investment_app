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