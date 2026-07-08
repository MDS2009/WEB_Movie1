from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views, telegram_views
from .forms import LoginForm

app_name = 'users'

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='users/login.html',
            authentication_form=LoginForm,
        ),
        name='login',
    ),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/<str:token>/', views.password_reset_confirm, name='password_reset_confirm_direct'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('favorites/', views.favorites, name='favorites'),
    path('create-community/', views.create_community, name='create_community'),
    path('edit-community/<int:community_id>/', views.edit_community, name='edit_community'),
    path('manage-community/<int:community_id>/', views.manage_community, name='manage_community'),
    path('manage-members/<int:community_id>/', views.manage_members, name='manage_members'),
    path('telegram/connect/', telegram_views.telegram_connect, name='telegram_connect'),
    path('telegram/disconnect/', telegram_views.telegram_disconnect, name='telegram_disconnect'),
    path('telegram/webhook/', telegram_views.telegram_webhook, name='telegram_webhook'),
    path('', views.logout_view, name='logout'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('data-processing-consent/', views.data_processing_consent, name='data_processing_consent'),
]
