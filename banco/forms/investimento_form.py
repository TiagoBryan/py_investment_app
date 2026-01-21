from django import forms


class CriarPerfilInvestidorForm(forms.Form):
    PERFIL_CHOICES = [
        ("CONSERVADOR", "Conservador (Baixo Risco)"),
        ("MODERADO", "Moderado (Médio Risco)"),
        ("ARROJADO", "Arrojado (Alto Risco)"),
    ]

    perfil_investidor = forms.ChoiceField(
        label="Qual seu perfil de investidor?",
        choices=PERFIL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    patrimonio_total = forms.DecimalField(
        label="Patrimônio Inicial (R$)",
        min_value=0.00,
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-input', 
                                        'placeholder': '0.00'})
    )


class RealizarInvestimentoForm(forms.Form):
    TIPO_CHOICES = [
        ("RENDA_FIXA", "Renda Fixa"),
        ("ACOES", "Ações"),
        ("FUNDOS", "Fundos"),
        ("CRIPTO", "Criptomoedas"),
    ]

    tipo_investimento = forms.ChoiceField(
        label="Onde você quer investir?",
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    valor_investido = forms.DecimalField(
        label="Valor do Aporte (R$)",
        min_value=1.00,  # Investimento mínimo
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-input', 
                                        'placeholder': '0.00'})
    )