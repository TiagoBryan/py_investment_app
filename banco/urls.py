from django.urls import path
from . import views 

urlpatterns = [
    # --- Landing e Home ---
    path('', views.LandingFrontEnd.as_view(), name='landing_page'),
    path('home/', views.HomeFrontEnd.as_view(), name='home_page'),

    # --- Autenticação (Login/Logout) ---
    path('login/', views.LoginFrontEnd.as_view(), name='login_page'),
    path('logout/', views.LogoutFrontEnd.as_view(), name='logout_page'),

    # --- Cadastro (Signup) ---
    path('signup/', views.SignupFrontEnd.as_view(), name='signup_page'),
    path('signup/email_sent/', views.SignupEmailSentFrontEnd.as_view(), 
         name='signup_email_sent_page'),
    path('signup/verify/', views.SignupVerifyFrontEnd.as_view(), 
         name='signup_verify_page'),
    path('signup/verified/', views.SignupVerifiedFrontEnd.as_view(), 
         name='signup_verified_page'),
    path('signup/not_verified/', views.SignupNotVerifiedFrontEnd.as_view(), 
         name='signup_not_verified_page'),

    # --- Reset de Senha (Esqueci a senha) ---
    path('password/reset/', views.PasswordResetFrontEnd.as_view(), 
         name='password_reset_page'),
    path('password/reset/email_sent/', views.PasswordResetEmailSentFrontEnd.
         as_view(), name='password_reset_email_sent_page'),
    path('password/reset/verify/', views.PasswordResetVerifyFrontEnd.as_view(), 
         name='password_reset_verify_page'),
    path('password/reset/verified/', views.PasswordResetVerifiedFrontEnd.
         as_view(), name='password_reset_verified_page'),
    path('password/reset/not_verified/', views.
         PasswordResetNotVerifiedFrontEnd.as_view(), 
         name='password_reset_not_verified_page'),
    path('password/reset/success/', views.
         PasswordResetSuccessFrontEnd.as_view(), 
         name='password_reset_success_page'),

    # --- Troca de Senha (Usuário Logado) ---
    path('password/change/', views.PasswordChangeFrontEnd.as_view(), 
         name='password_change_page'),
    path('password/change/success/', views.
         PasswordChangeSuccessFrontEnd.as_view(), 
         name='password_change_success_page'),

    # --- Troca de Email ---
    path('email/change/', views.EmailChangeFrontEnd.as_view(), 
         name='email_change_page'),
    path('email/change/emails_sent/', views.
         EmailChangeEmailsSentFrontEnd.as_view(), 
         name='email_change_emails_sent_page'),
    path('email/change/verify/', views.EmailChangeVerifyFrontEnd.as_view(), 
         name='email_change_verify_page'),
    path('email/change/verified/', views.EmailChangeVerifiedFrontEnd.as_view(), 
         name='email_change_verified_page'),
    path('email/change/not_verified/', views.
         EmailChangeNotVerifiedFrontEnd.as_view(), 
         name='email_change_not_verified_page'),

    # --- Dados do Usuário (Nome/Sobrenome) ---
    path('users/me/change/', views.UsersMeChangeFrontEnd.as_view(), 
         name='users_me_change_page'),
    path('users/me/change/success/', views.
         UsersMeChangeSuccessFrontEnd.as_view(), 
         name='users_me_change_success_page'),

    # --- Conta Corrente (Criar/Desativar) ---
    path('conta-corrente/criar/', views.
         CriarContaCorrenteFrontEnd.as_view(), name='conta_criar_page'),
    path('contas/<int:conta_id>/desativar/', views.
         ContaCorrenteDeactivateFrontEnd.as_view(), 
         name='conta_desativar_page'),

    # --- Movimentações e Score ---
    path("conta/deposito/", views.DepositoFrontEnd.as_view(), 
         name="deposito_page"),
    path("conta/saque/", views.SaqueFrontEnd.as_view(), name="saque_page"),
    path("conta/score/", views.ScoreCreditoFrontEnd.as_view(), 
         name="score_page"),

    # --- Desativação do Usuário ---
    path('users/me/desativar/', views.UserDeactivateFrontEnd.as_view(), 
         name='user_deactivate_page'),
    
    # --- Investimentos ---
    path('investimentos/me/', views.DashboardInvestimentosFrontEnd.as_view(), 
         name='investimentos_dashboard_page'),
    path('investimentos/criar-perfil/', views.CriarPerfilInvestidorFrontEnd.
         as_view(), name='criar_perfil_investidor_page'),
    
    path('investimentos/carteira/', 
         views.ListarInvestimentosFrontEnd.as_view(), 
         name='listar_investimentos_page'),


    path('investimentos/novo/', views.RealizarInvestimentoFrontEnd.as_view(), 
         name='realizar_investimento_page'),

    path('investimentos/<uuid:investimento_id>/resgatar/', 
         views.ResgatarInvestimentoFrontEnd.as_view(), 
         name='resgatar_investimento_page'),
]