from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views
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
    path('oauth/yandex/', views.yandex_login, name='yandex_login'),
    path('oauth/yandex/callback/', views.yandex_callback, name='yandex_callback'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset_request.html',
            email_template_name='users/password_reset_email.txt',
            subject_template_name='users/password_reset_subject.txt',
            success_url=reverse_lazy('users:password_reset_done'),
        ),
        name='password_reset_request',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_email_sent.html'),
        name='password_reset_done',
    ),
    path(
        'password-reset/confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_form.html',
            success_url=reverse_lazy('users:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_done.html'),
        name='password_reset_complete',
    ),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('favorites/', views.favorites, name='favorites'),
    path('my-communities/', views.my_communities, name='my_communities'),
    path('create-community/', views.create_community, name='create_community'),
    path('edit-community/<int:community_id>/', views.edit_community, name='edit_community'),
    path('manage-community/<int:community_id>/', views.manage_community, name='manage_community'),
    path('manage-members/<int:community_id>/', views.manage_members, name='manage_members'),
    path('', views.logout_view, name='logout'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('data-processing-consent/', views.data_processing_consent, name='data_processing_consent'),
]
