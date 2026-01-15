import requests
from django.conf import settings
from django.contrib.auth import get_user_model, logout
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.urls import reverse


User = get_user_model()


class LogoutFrontEnd(View):
    def get(self, request):
        token = request.session.get('auth_token')

        if token:
            url = f"{settings.API_BASE_URL}/logout/"
            headers = {'Authorization': f'Token {token}'}
            try:
                requests.get(url, headers=headers)
            except requests.RequestException:
                pass

        logout(request)
        
        request.session.flush()

        return HttpResponseRedirect(reverse('landing_page'))