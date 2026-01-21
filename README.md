# PYInvest Web Client (Frontend) 💻

Aplicação Web desenvolvida em **Django** que atua como interface para o PYInvest API. Este projeto não possui banco de dados de negócio local; ele consome todos os dados e regras via requisições HTTP para a API Backend.

## 🚀 Funcionalidades

- **Interface do Usuário:** Templates Django renderizados no servidor.
- **Consumo de API:** Uso da biblioteca `requests` para comunicação com o Backend.
- **Sessão Híbrida:** Sistema de login que sincroniza a sessão do Django com o Token da API.
- **Formulários:** Validação de formato e feedback de erros vindos da API.
- **Área do Cliente:**
  - Dashboard com saldo e score.
  - Extrato visual.
  - Configurações de perfil (Troca de senha, e-mail, encerramento de conta).

## ⚠️ Pré-requisitos

Para que este projeto funcione, a **PYInvest API** deve estar rodando.
Certifique-se de baixar e rodar o repositório da API na porta `8000` (ou configurar a URL correta).

## 🛠️ Tecnologias

- Python 3.12+
- Django 5+
- Requests
- HTML5 / CSS3

## ⚙️ Instalação e Execução

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/TiagoBryan/Javer-Bank-App.git
   cd Javer-Bank-App
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuração da API:**
   No arquivo `settings.py`, verifique a variável `API_BASE_URL`. Ela deve apontar para onde sua API está rodando:
   ```python
   # settings.py
   API_BASE_URL = 'http://127.0.0.1:8000/api'
   ```

5. **Execute as migrações (Apenas para Sessão/Auth local):**
   *Nota: Este projeto usa SQLite apenas para gerenciar sessões de login do navegador, nenhum dado bancário é salvo aqui.*
   ```bash
   python manage.py migrate
   ```

6. **Inicie o servidor (Em uma porta diferente da API):**
   ```bash
   python manage.py runserver 8001
   ```
   Acesse o sistema em `http://127.0.0.1:8001/`.

## 🧪 Testes

Os testes deste projeto utilizam `Mock` para simular as respostas da API, garantindo que o Frontend funcione corretamente independente do Backend estar online durante os testes.

```bash
python manage.py test
```

## 📂 Estrutura de Comunicação

O Frontend segue o padrão de **Consumer**:

1. **Formulário** recebe dados do usuário.
2. **View** valida formatos básicos.
3. **Requests** envia payload JSON para a API (ex: `POST /api/login/`).
4. **API** processa e retorna Sucesso (200/201) ou Erro (400/500).
5. **View** trata a resposta e exibe mensagens de sucesso ou erros de validação no template.

---