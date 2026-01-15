import requests
from django.conf import settings
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from banco.forms import DepositoForm, SaqueForm


class DepositoFrontEnd(FormView):
    template_name = "movimentacao_templates/deposito.html"
    form_class = DepositoForm
    success_url = reverse_lazy("home_page")

    def form_valid(self, form):
        valor = float(form.cleaned_data["valor"])
        
        token = self.request.session.get('auth_token')
        headers = {'Authorization': f'Token {token}'}
        payload = {'valor': valor}
        
        url = f"{settings.API_BASE_URL}/conta/deposito/"

        try:
            response = requests.post(url, json=payload, headers=headers)
        except requests.RequestException:
            form.add_error(None, "Erro de conexão com o servidor.")
            return self.form_invalid(form)

        if response.status_code == 200:
            messages.success(self.request, "Depósito realizado com sucesso!")
            return super().form_valid(form)
        else:
            try:
                data = response.json()
                if 'detail' in data:
                    form.add_error(None, data['detail'])
                else:
                    form.add_error(None, "Erro ao realizar depósito.")
            except Exception as e:
                form.add_error(e, "Erro desconhecido.")
            
            return self.form_invalid(form)


class SaqueFrontEnd(FormView):
    template_name = "movimentacao_templates/saque.html"
    form_class = SaqueForm
    success_url = reverse_lazy("home_page")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        token = self.request.session.get('auth_token')
        if token:
            headers = {'Authorization': f'Token {token}'}
            url = f"{settings.API_BASE_URL}/conta/score/"
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    context["saldo"] = data.get("saldo")
            except requests.RequestException:
                context["saldo"] = "---"
        
        return context

    def form_valid(self, form):
        valor = float(form.cleaned_data["valor"])

        token = self.request.session.get('auth_token')
        headers = {'Authorization': f'Token {token}'}
        payload = {'valor': valor}

        url = f"{settings.API_BASE_URL}/conta/saque/"

        try:
            response = requests.post(url, json=payload, headers=headers)
        except requests.RequestException:
            form.add_error(None, "Erro de conexão com o servidor.")
            return self.form_invalid(form)

        if response.status_code == 200:
            messages.success(self.request, "Saque realizado com sucesso!")
            return super().form_valid(form)
        
        elif response.status_code == 400:
            try:
                data = response.json()
                detail = data.get('detail', '')
                
                if "Saldo insuficiente" in detail:
                    form.add_error('valor', "Saldo insuficiente.")
                else:
                    form.add_error(None, detail)
            except Exception as e:
                form.add_error(e, "Erro ao processar saque.")
            
            return self.form_invalid(form)
            
        else:
            form.add_error(None, "Erro inesperado.")
            return self.form_invalid(form)