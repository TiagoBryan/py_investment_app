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
        ("ACOES", "Ações (B3/EUA)"),
        ("FUNDOS", "Fundos Imobiliários (FIIs)"),
        ("CRIPTO", "Criptomoedas"),
    ]

    tipo_investimento = forms.ChoiceField(
        label="Tipo de Ativo",
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input', 
                                   'id': 'tipo_investimento'})
    )

    ticker = forms.CharField(
        label="Código do Ativo (Ticker)",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input', 
            'placeholder': 'Ex: PETR4, BTC-USD',
            'style': 'text-transform: uppercase;'
        })
    )

    quantidade = forms.DecimalField(
        label="Quantidade",
        required=False,
        min_value=0.00000001,
        decimal_places=8,
        widget=forms.NumberInput(attrs={'class': 'form-input', 
                                        'placeholder': '0.0'})
    )

    valor_investido = forms.DecimalField(
        label="Valor do Aporte (R$)",
        required=False,
        min_value=1.00,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-input', 
                                        'placeholder': '0.00'})
    )

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo_investimento")
        ticker = cleaned_data.get("ticker")
        qtd = cleaned_data.get("quantidade")
        valor = cleaned_data.get("valor_investido")

        if tipo in ['ACOES', 'FUNDOS', 'CRIPTO']:
            if not ticker:
                self.add_error('ticker', 
                               "Para este tipo, o Ticker é obrigatório.")
            if not qtd:
                self.add_error('quantidade', "Informe a quantidade desejada.")
        
        elif tipo == 'RENDA_FIXA':
            if not valor:
                self.add_error('valor_investido', 
                               "Para Renda Fixa, informe o valor do aporte.")
        
        return cleaned_data


class AtualizarPerfilInvestidorForm(forms.Form):
    PERFIL_CHOICES = [
        ("CONSERVADOR", "Conservador (Baixo Risco)"),
        ("MODERADO", "Moderado (Médio Risco)"),
        ("ARROJADO", "Arrojado (Alto Risco)"),
    ]

    perfil_investidor = forms.ChoiceField(
        label="Novo Perfil Desejado",
        choices=PERFIL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )