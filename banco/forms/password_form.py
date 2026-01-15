from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


class PasswordConfirmForm(forms.Form):
    password = forms.CharField(
        label=_("Nova Senha"),
        max_length=128,
        widget=forms.PasswordInput,
        help_text=_("A senha deve ter no mínimo 8 caracteres e não ser muito "
                    "comum.")
    )
    password2 = forms.CharField(
        label=_("Confirme a Senha"),
        max_length=128,
        widget=forms.PasswordInput
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        if password:
            try:
                validate_password(password, user=self.user)
            except ValidationError as e:
                raise forms.ValidationError(e.messages)  # type: ignore
        
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            self.add_error('password2', _("As senhas não conferem."))

        return cleaned_data


class PasswordResetForm(forms.Form):
    email = forms.EmailField(max_length=255, label=_("E-mail"))


class PasswordResetVerifiedForm(PasswordConfirmForm):
    pass


class PasswordChangeForm(PasswordConfirmForm):
    pass