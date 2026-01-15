import requests
from django.conf import settings
from django.views.generic.edit import FormView
from django.views.generic import TemplateView, View
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages

from banco.forms import (
    PasswordResetForm, 
    PasswordResetVerifiedForm, 
    PasswordChangeForm
)


class PasswordResetFrontEnd(FormView):
    template_name = 'password_templates/password_reset.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_email_sent_page')

    def form_valid(self, form):
        email = form.cleaned_data['email']

        url = f"{settings.API_BASE_URL}/password/reset/"
        payload = {'email': email}

        try:
            response = requests.post(url, json=payload)
        except requests.RequestException:
            form.add_error(None, "Erro de conexão com o servidor.")
            return self.form_invalid(form)

        if response.status_code == 201:
            return super().form_valid(form)
        
        else:
            try:
                data = response.json()
                if 'detail' in data:
                    form.add_error(None, data['detail'])
                else:
                    form.add_error(None, "Não foi possível processar o "
                                         "reset de senha.")
            except Exception as e:
                form.add_error(e, "Erro desconhecido.")
            
            return self.form_invalid(form)


class PasswordResetEmailSentFrontEnd(TemplateView):
    template_name = 'password_templates/password_reset_email_sent.html'


class PasswordResetVerifyFrontEnd(View):
    def get(self, request, format=None):
        code = request.GET.get('code', '')

        url = f"{settings.API_BASE_URL}/password/reset/verify/"
        
        try:
            response = requests.get(url, params={'code': code})
            
            if response.status_code == 200:
                request.session['password_reset_code'] = code
                return HttpResponseRedirect(
                    reverse('password_reset_verified_page'))
            else:
                return HttpResponseRedirect(
                    reverse('password_reset_not_verified_page'))
                
        except requests.RequestException:
            return HttpResponseRedirect(
                 reverse('password_reset_not_verified_page'))


class PasswordResetVerifiedFrontEnd(FormView):
    """
    Formulário onde o usuário digita a nova senha.
    """
    template_name = 'password_templates/password_reset_verified.html'
    form_class = PasswordResetVerifiedForm
    success_url = reverse_lazy('password_reset_success_page')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = None 
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if 'password_reset_code' not in request.session:
            return redirect('password_reset_page')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        code = self.request.session['password_reset_code']
        password = form.cleaned_data['password']

        url = f"{settings.API_BASE_URL}/password/reset/verified/"
        payload = {
            'code': code,
            'password': password
        }

        try:
            response = requests.post(url, json=payload)
        except requests.RequestException:
            form.add_error(None, "Erro de conexão.")
            return self.form_invalid(form)

        if response.status_code == 200:
            del self.request.session['password_reset_code']
            return super().form_valid(form)
        
        else:
            try:
                errors = response.json()
                if 'detail' in errors:
                    form.add_error(None, errors['detail'])
                
                if 'password' in errors:
                    form.add_error('password', errors['password'][0])
            except Exception as e:
                form.add_error(e, "Erro ao redefinir senha.")
            
            return self.form_invalid(form)


class PasswordResetNotVerifiedFrontEnd(TemplateView):
    template_name = 'password_templates/password_reset_not_verified.html'


class PasswordResetSuccessFrontEnd(TemplateView):
    template_name = 'password_templates/password_reset_success.html'


class PasswordChangeFrontEnd(FormView):
    """
    Troca de senha para usuário LOGADO.
    """
    template_name = 'password_templates/password_change.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_success_page')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user 
        return kwargs

    def form_valid(self, form):
        token = self.request.session.get('auth_token')
        if not token:
            return redirect('login_page')

        password = form.cleaned_data['password']

        url = f"{settings.API_BASE_URL}/password/change/"
        headers = {'Authorization': f'Token {token}'}
        payload = {'password': password}

        try:
            response = requests.post(url, json=payload, headers=headers)
        except requests.RequestException:
            form.add_error(None, "Erro de conexão.")
            return self.form_invalid(form)

        if response.status_code == 200:
            messages.success(self.request, "Senha alterada com sucesso.")
            return super().form_valid(form)
        
        else:
            try:
                errors = response.json()
                if 'detail' in errors:
                    form.add_error(None, errors['detail'])
                
                if 'password' in errors:
                    form.add_error('password', errors['password'][0])
            except Exception as e:
                form.add_error(e, "Erro ao alterar senha.")
            
            return self.form_invalid(form)


class PasswordChangeSuccessFrontEnd(TemplateView):
    template_name = 'password_templates/password_change_success.html'