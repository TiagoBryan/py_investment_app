import requests
from django.conf import settings
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth import login, get_user_model
from banco.forms import LoginForm

User = get_user_model()


class LoginFrontEnd(FormView):
    template_name = 'login_templates/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home_page')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        cpf_cnpj = form.cleaned_data['cpf_cnpj']

        url = f"{settings.API_BASE_URL}/login/custom/"

        payload = {
            'email': email,
            'password': password,
            'cpf_cnpj': cpf_cnpj
        }

        try:
            response = requests.post(url, json=payload)
        except requests.RequestException:
            form.add_error(None, "Erro de conexão com o servidor.")
            return self.form_invalid(form)

        if response.status_code == 200:
            data = response.json()
            token = data.get('token')

            self.request.session['auth_token'] = token

            headers = {'Authorization': f'Token {token}'}
            try:
                user_response = requests.\
                    get(f"{settings.API_BASE_URL}/users/me/", headers=headers)
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    first_name = user_data.get('first_name', '')
                    last_name = user_data.get('last_name', '')

                    user_local, created = User.objects.get_or_create(
                        email=email,
                        defaults={
                            'username': email,
                            'first_name': first_name,
                            'last_name': last_name
                        }
                    )

                    if not created:
                        user_local.first_name = first_name
                        user_local.last_name = last_name
                        user_local.save()

                    login(self.request, user_local)

            except requests.RequestException:
                pass

            return super().form_valid(form)

        else:
            try:
                data = response.json()
                if 'non_field_errors' in data:
                    form.add_error(None, data['non_field_errors'][0])
                elif 'detail' in data:
                    form.add_error(None, data['detail'])
                else:
                    form.add_error(None, "Credenciais ou CPF inválidos.")
            except Exception as e:
                form.add_error(e, "Erro ao autenticar.")

            return self.form_invalid(form)
