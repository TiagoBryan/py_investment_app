import requests
from django.conf import settings
from django.views.generic.edit import FormView
from django.views.generic import TemplateView, View
from django.urls import reverse_lazy
from django.shortcuts import redirect
from banco.forms import SignupForm


class SignupFrontEnd(FormView):
    template_name = 'signup_templates/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('signup_email_sent_page')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = None
        return kwargs

    def form_valid(self, form):

        payload = form.cleaned_data
        
        url = f"{settings.API_BASE_URL}/signup/cliente/"
        
        try:
    
            response = requests.post(url, json=payload)
        except requests.RequestException:
            form.add_error(None, "Erro de conexão com o servidor.")
            return self.form_invalid(form)

        if response.status_code == 201:
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
                    elif field != 'detail':
                        form.add_error(None, f"{field}: {msgs}")
            except Exception as e:
                form.add_error(e, "Erro desconhecido ao criar cadastro.")
            
            return self.form_invalid(form)
        
    def form_invalid(self, form):
        return super().form_invalid(form)


class SignupEmailSentFrontEnd(TemplateView):
    template_name = 'signup_templates/signup_email_sent.html'


class SignupVerifyFrontEnd(View):
    def get(self, request, format=None):
        code = request.GET.get('code', '')
        
        url = f"{settings.API_BASE_URL}/signup/verify/"
        
        try:
            response = requests.get(url, params={'code': code})
            
            if response.status_code == 200:
                return redirect('signup_verified_page')
            else:
                return redirect('signup_not_verified_page')
                
        except requests.RequestException:
            return redirect('signup_not_verified_page')


class SignupVerifiedFrontEnd(TemplateView):
    template_name = 'signup_templates/signup_verified.html'


class SignupNotVerifiedFrontEnd(TemplateView):
    template_name = 'signup_templates/signup_not_verified.html'