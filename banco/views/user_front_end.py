import requests
from django.conf import settings
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from banco.forms import UsersMeChangeForm
from django.contrib.auth import logout
from banco.forms import UserDeactivateForm
from django.shortcuts import redirect


class UsersMeChangeFrontEnd(FormView):
    template_name = 'user_templates/users_me_change.html'
    form_class = UsersMeChangeForm
    success_url = reverse_lazy('users_me_change_success_page')

    def get_token_header(self):
        token = self.request.session.get('auth_token')
        return {'Authorization': f'Token {token}'} if token else {}

    def get_initial(self):
        """
        Preenche os campos do formulário com os dados atuais da API.
        """
        initial = super().get_initial()
        
        url = f"{settings.API_BASE_URL}/users/me/"
        headers = self.get_token_header()

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                initial['first_name'] = data.get('first_name', '')
                initial['last_name'] = data.get('last_name', '')
        except requests.RequestException:
            pass
            
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        initial_data = self.get_initial()
        context['first_name'] = initial_data.get('first_name')
        context['last_name'] = initial_data.get('last_name')
        
        return context

    def form_valid(self, form):
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']

        payload = {
            'first_name': first_name,
            'last_name': last_name
        }

        url = f"{settings.API_BASE_URL}/users/me/change/"
        headers = self.get_token_header()

        try:
            response = requests.post(url, json=payload, headers=headers)
        except requests.RequestException:
            form.add_error(None, "Erro de conexão com o servidor.")
            return self.form_invalid(form)

        if response.status_code == 200:
            messages.success(self.request, "Dados atualizados com sucesso!")
            return super().form_valid(form)
        
        else:
            try:
                errors = response.json()
                if 'detail' in errors:
                    form.add_error(None, errors['detail'])
                
                for field, msgs in errors.items():
                    if field in form.fields:
                        for msg in msgs:
                            form.add_error(field, msg)
            except Exception as e:
                form.add_error(e, "Erro desconhecido ao atualizar dados.")
            
            return self.form_invalid(form)


class UsersMeChangeSuccessFrontEnd(TemplateView):
    template_name = 'user_templates/users_me_change_success.html'


class UserDeactivateFrontEnd(FormView):
    template_name = 'user_templates/desativar_usuario.html'
    form_class = UserDeactivateForm
    success_url = reverse_lazy('landing_page')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_page')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        token = self.request.session.get('auth_token')
        password = form.cleaned_data['password']
        
        url = f"{settings.API_BASE_URL}/users/me/desativar/"
        headers = {'Authorization': f'Token {token}'}
        payload = {'password': password}

        try:
            response = requests.post(url, json=payload, headers=headers)
        except requests.RequestException:
            form.add_error(None, "Erro de conexão com o servidor.")
            return self.form_invalid(form)

        if response.status_code == 200:
            if 'auth_token' in self.request.session:
                del self.request.session['auth_token']
            
            logout(self.request)
            
            return redirect('landing_page')
        
        else:
            try:
                data = response.json()
                if 'detail' in data:
                    form.add_error(None, data['detail'])
                
                if 'password' in data:
                    form.add_error('password', data['password'][0])
            except Exception as e:
                form.add_error(e, "Erro ao tentar desativar usuário.")
            
            return self.form_invalid(form)