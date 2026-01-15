from django import forms
from django.utils.translation import gettext_lazy as _


class EmailChangeForm(forms.Form):
    email = forms.EmailField(
        max_length=255, 
        label=_("Novo E-mail"),
        widget=forms.EmailInput(attrs={'placeholder': 'exemplo@email.com'})
    )