import requests
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib import messages
from banco.forms import ContaCorrenteForm, ContaCorrenteDeactivateForm
from django.http import Http404


class CriarContaCorrenteFrontEnd(FormView):
    template_name = "conta_templates/criar_conta.html"
    form_class = ContaCorrenteForm
    success_url = reverse_lazy("home_page")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login_page")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        payload = {
            'agencia': form.cleaned_data['agencia'],
            'numero': form.cleaned_data['numero']
        }

        token = self.request.session.get('auth_token') 
        headers = {'Authorization': f'Token {token}'}

        try:
            response = requests.post(
                f"{settings.API_BASE_URL}/contas/",
                json=payload,
                headers=headers
            )
        except requests.RequestException:
            form.add_error(None, "Erro de conexão com o servidor.")
            return self.form_invalid(form)

        if response.status_code == 201:
            messages.success(self.request, "Conta criada com sucesso!")
            return super().form_valid(form)
        
        else:
            try:
                errors = response.json()
                if 'detail' in errors:
                    form.add_error(None, errors['detail'])
                elif isinstance(errors, dict):
                    for field, msg_list in errors.items():
                        if field in form.fields:
                            for msg in msg_list:
                                form.add_error(field, msg)
                        else:
                            for msg in msg_list:
                                form.add_error(None, msg)
            except Exception as a:
                form.add_error(a, "Ocorreu um erro desconhecido na API.")
            
            return self.form_invalid(form)


class ContaCorrenteDeactivateFrontEnd(FormView):
    template_name = 'conta_templates/desativar_conta.html'
    form_class = ContaCorrenteDeactivateForm
    success_url = reverse_lazy('home_page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        token = self.request.session.get('auth_token')
        if not token:
            return context

        headers = {'Authorization': f'Token {token}'}

        total_investido = 0.0
        meu_perfil = None

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

        try:
            url_perfil = f"{settings.API_BASE_URL}/internal/clientes/" 
            resp_perfil = requests.get(url_perfil, headers=headers)
                     
            if resp_perfil.status_code == 200:
                clientes = resp_perfil.json()
                if clientes:
                    meu_perfil = clientes[0]
                    
                    cliente_id = meu_perfil['id']
                    
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

        except Exception as e:
            print(f"Erro no dashboard: {e}")
            context['error'] = "Serviço de investimentos indisponível no " \
                               "momento."
        
        context['total_investido'] = total_investido
            
        return context

    def form_valid(self, form):
        conta_id = self.kwargs['conta_id'] 
        password = form.cleaned_data['password']
        
        payload = {'password': password}
        token = self.request.session.get('auth_token')
        headers = {'Authorization': f'Token {token}'}

        url = f"{settings.API_BASE_URL}/contas/{conta_id}/desativar/"
        
        try:
            response = requests.post(url, json=payload, headers=headers)
        except requests.RequestException:
            form.add_error(None, "Erro de conexão com a API.")
            return self.form_invalid(form)

        if response.status_code == 200:
            messages.success(self.request, "Conta desativada com sucesso.")
            return super().form_valid(form)
        else:
            try:
                errors = response.json()
                if 'password' in errors:
                    form.add_error('password', errors['password'][0]) 
                elif 'detail' in errors:
                    form.add_error(None, errors['detail'])
                elif 'error' in errors:
                    form.add_error(None, errors['error'])
                else:
                    form.add_error(None, "Erro ao desativar conta.")
            except Exception as e:
                form.add_error(e, "Erro desconhecido.")
            return self.form_invalid(form)