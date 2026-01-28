import requests
from django.conf import settings
from django.views.generic.edit import FormView
from django.views.generic import TemplateView, View
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from banco.forms import EmailChangeForm


class EmailChangeFrontEnd(FormView):
    template_name = 'email_templates/email_change.html'
    form_class = EmailChangeForm
    success_url = reverse_lazy('email_change_emails_sent_page')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_page')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        token = self.request.session.get('auth_token')
        email = form.cleaned_data['email']

        url = f"{settings.API_BASE_URL}/email/change/"
        headers = {'Authorization': f'Token {token}'}
        payload = {'email': email}

        try:
            response = requests.post(url, json=payload, headers=headers)
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
                
                if 'email' in data:
                    form.add_error('email', data['email'][0])
            except Exception as e:
                form.add_error(e, "Erro ao solicitar troca de e-mail.")
            
            return self.form_invalid(form)


class EmailChangeEmailsSentFrontEnd(TemplateView):
    template_name = 'email_templates/email_change_emails_sent.html'


class EmailChangeVerifyFrontEnd(View):
    """
    recebe o clique do link do e-mail: /email/change/verify/?code=XYZ
    """
    def get(self, request, format=None):
        code = request.GET.get('code', '')

        url = f"{settings.API_BASE_URL}/email/change/verify/"
        
        try:
            response = requests.get(url, params={'code': code})

            if response.status_code == 200:
                return HttpResponseRedirect(
                    reverse('email_change_verified_page'))
            else:
                return HttpResponseRedirect(
                    reverse('email_change_not_verified_page'))

        except requests.RequestException:
            return HttpResponseRedirect(
                reverse('email_change_not_verified_page'))


class EmailChangeVerifiedFrontEnd(TemplateView):
    template_name = 'email_templates/email_change_verified.html'


class EmailChangeNotVerifiedFrontEnd(TemplateView):
    template_name = 'email_templates/email_change_not_verified.html'